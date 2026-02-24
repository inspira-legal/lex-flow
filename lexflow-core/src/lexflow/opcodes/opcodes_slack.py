"""Slack opcodes for LexFlow.

This module provides opcodes for interacting with Slack's Web API,
enabling automation workflows similar to n8n.

Installation:
    pip install lexflow[slack]

Authentication:
    Requires a Slack Bot Token (xoxb-...) or User Token (xoxp-...):
    - Create a Slack App at https://api.slack.com/apps
    - Add required OAuth scopes based on desired functionality
    - Install to workspace and copy the Bot Token

Required Scopes (depending on opcodes used):
    Messages: chat:write, chat:write.public
    Channels: channels:read, channels:write, channels:manage
    Users: users:read
    Files: files:read, files:write
    Reactions: reactions:read, reactions:write
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp

from .opcodes import opcode, register_category

if TYPE_CHECKING:
    from slack_sdk.web.async_client import AsyncWebClient

try:
    from slack_sdk.web.async_client import AsyncWebClient
    from slack_sdk.errors import SlackApiError

    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    SlackApiError = Exception


def register_slack_opcodes():
    """Register Slack opcodes to the default registry."""

    # Register webhook opcode outside SLACK_AVAILABLE guard (only needs aiohttp)
    register_category(
        id="slack",
        label="Slack",
        prefix="slack_",
        color="#4A154B",
        icon="💬",
        requires="slack",
        order=280,
    )

    @opcode(category="slack")
    async def slack_send_webhook(
        url: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> bool:
        """Send a message via incoming webhook.

        Args:
            url: Incoming webhook URL (must be https://hooks.slack.com/...)
            text: Message text (required, used as fallback)
            blocks: Optional Block Kit blocks
            username: Optional custom username
            icon_emoji: Optional emoji for bot icon (e.g., ":robot_face:")
            icon_url: Optional URL for bot icon
            timeout: Request timeout in seconds (default: 30)

        Returns:
            True if successful

        Note: Does not require a Slack client, uses webhook directly
        """
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError("Webhook URL must use HTTPS")
        if parsed.hostname != "hooks.slack.com":
            raise ValueError(f"Webhook URL host not allowed: {parsed.hostname}")

        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if icon_url:
            payload["icon_url"] = icon_url

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise RuntimeError(f"Webhook failed with status {response.status}")
                return True

    if not SLACK_AVAILABLE:
        return

    # =========================================================================
    # Client Management
    # =========================================================================

    @opcode(category="slack")
    async def slack_create_client(token: str) -> AsyncWebClient:
        """Create a Slack Web API client.

        Args:
            token: Slack Bot Token (xoxb-...) or User Token (xoxp-...)

        Returns:
            AsyncWebClient instance for use with other Slack opcodes

        Example:
            token: "xoxb-your-bot-token"
        """
        return AsyncWebClient(token=token)

    # =========================================================================
    # Message Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_send_message(
        client: AsyncWebClient,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        broadcast: bool = False,
        unfurl_links: bool = True,
        unfurl_media: bool = True,
    ) -> Dict[str, Any]:
        """Send a message to a channel, user, or thread.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID, channel name, or user ID
            text: Message text (supports Slack markdown)
            thread_ts: Optional thread timestamp to reply in thread
            broadcast: Whether to also post to channel when replying in thread (default: False)
            unfurl_links: Whether to unfurl URLs (default: True)
            unfurl_media: Whether to unfurl media (default: True)

        Returns:
            Dict with: ok, channel, ts, message

        Required scopes: chat:write, chat:write.public (for public channels)
        """
        try:
            kwargs = {
                "channel": channel,
                "text": text,
                "unfurl_links": unfurl_links,
                "unfurl_media": unfurl_media,
            }
            if thread_ts is not None:
                kwargs["thread_ts"] = thread_ts
            if broadcast:
                kwargs["reply_broadcast"] = broadcast

            response = await client.chat_postMessage(**kwargs)
            return {
                "ok": response["ok"],
                "channel": response["channel"],
                "ts": response["ts"],
                "message": response.get("message", {}),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_send_blocks(
        client: AsyncWebClient,
        channel: str,
        blocks: List[Dict[str, Any]],
        text: str = "",
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message with Block Kit blocks.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID or channel name
            blocks: List of Block Kit block objects
            text: Fallback text for notifications (recommended)
            thread_ts: Optional thread timestamp to reply in thread

        Returns:
            Dict with: ok, channel, ts, message

        Required scopes: chat:write

        See: https://api.slack.com/block-kit
        """
        try:
            kwargs = {
                "channel": channel,
                "blocks": blocks,
                "text": text,
            }
            if thread_ts is not None:
                kwargs["thread_ts"] = thread_ts

            response = await client.chat_postMessage(**kwargs)
            return {
                "ok": response["ok"],
                "channel": response["channel"],
                "ts": response["ts"],
                "message": response.get("message", {}),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_update_message(
        client: AsyncWebClient,
        channel: str,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Update an existing message.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the message exists
            ts: Timestamp of the message to update
            text: New message text (optional if blocks provided)
            blocks: New Block Kit blocks (optional)

        Returns:
            Dict with: ok, channel, ts, message

        Required scopes: chat:write
        """
        try:
            kwargs = {"channel": channel, "ts": ts}
            if text is not None:
                kwargs["text"] = text
            if blocks is not None:
                kwargs["blocks"] = blocks

            response = await client.chat_update(**kwargs)
            return {
                "ok": response["ok"],
                "channel": response["channel"],
                "ts": response["ts"],
                "message": response.get("message", {}),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_delete_message(
        client: AsyncWebClient,
        channel: str,
        ts: str,
    ) -> Dict[str, Any]:
        """Delete a message.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the message exists
            ts: Timestamp of the message to delete

        Returns:
            Dict with: ok, channel, ts

        Required scopes: chat:write
        """
        try:
            response = await client.chat_delete(channel=channel, ts=ts)
            return {
                "ok": response["ok"],
                "channel": response["channel"],
                "ts": response["ts"],
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_schedule_message(
        client: AsyncWebClient,
        channel: str,
        text: str,
        post_at: int,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a message for later delivery.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID or channel name
            text: Message text
            post_at: Unix timestamp for when to send the message
            thread_ts: Optional thread timestamp to reply in thread

        Returns:
            Dict with: ok, channel, scheduled_message_id, post_at

        Required scopes: chat:write
        """
        try:
            kwargs = {
                "channel": channel,
                "text": text,
                "post_at": post_at,
            }
            if thread_ts is not None:
                kwargs["thread_ts"] = thread_ts

            response = await client.chat_scheduleMessage(**kwargs)
            return {
                "ok": response["ok"],
                "channel": response["channel"],
                "scheduled_message_id": response["scheduled_message_id"],
                "post_at": response["post_at"],
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # Channel Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_list_channels(
        client: AsyncWebClient,
        types: Optional[str] = None,
        limit: int = 100,
        exclude_archived: bool = True,
    ) -> List[Dict[str, Any]]:
        """List channels in the workspace.

        Args:
            client: Slack client (from slack_create_client)
            types: Comma-separated channel types (public_channel, private_channel, mpim, im)
            limit: Maximum number of channels to return (default: 100)
            exclude_archived: Exclude archived channels (default: True)

        Returns:
            List of channel dicts with: id, name, is_private, is_archived, num_members

        Required scopes: channels:read, groups:read (for private), mpim:read, im:read
        """
        try:
            kwargs = {"limit": limit, "exclude_archived": exclude_archived}
            if types:
                kwargs["types"] = types
            response = await client.conversations_list(**kwargs)
            channels = []
            for ch in response.get("channels", []):
                channels.append(
                    {
                        "id": ch["id"],
                        "name": ch.get("name", ""),
                        "is_private": ch.get("is_private", False),
                        "is_archived": ch.get("is_archived", False),
                        "num_members": ch.get("num_members", 0),
                    }
                )
            return channels
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_create_channel(
        client: AsyncWebClient,
        name: str,
        is_private: bool = False,
    ) -> Dict[str, Any]:
        """Create a new channel.

        Args:
            client: Slack client (from slack_create_client)
            name: Channel name (lowercase, no spaces, max 80 chars)
            is_private: Whether to create a private channel (default: False)

        Returns:
            Dict with: id, name, is_private, created

        Required scopes: channels:manage, groups:write (for private)
        """
        try:
            response = await client.conversations_create(
                name=name,
                is_private=is_private,
            )
            ch = response["channel"]
            return {
                "id": ch["id"],
                "name": ch["name"],
                "is_private": ch.get("is_private", False),
                "created": ch.get("created", 0),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_archive_channel(
        client: AsyncWebClient,
        channel: str,
    ) -> bool:
        """Archive a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID to archive

        Returns:
            True if successful

        Required scopes: channels:manage, groups:write (for private)
        """
        try:
            await client.conversations_archive(channel=channel)
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_channel_info(
        client: AsyncWebClient,
        channel: str,
    ) -> Dict[str, Any]:
        """Get information about a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID

        Returns:
            Dict with: id, name, is_private, is_archived, topic, purpose, num_members, created

        Required scopes: channels:read, groups:read (for private)
        """
        try:
            response = await client.conversations_info(channel=channel)
            ch = response["channel"]
            return {
                "id": ch["id"],
                "name": ch.get("name", ""),
                "is_private": ch.get("is_private", False),
                "is_archived": ch.get("is_archived", False),
                "topic": ch.get("topic", {}).get("value", ""),
                "purpose": ch.get("purpose", {}).get("value", ""),
                "num_members": ch.get("num_members", 0),
                "created": ch.get("created", 0),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_invite_to_channel(
        client: AsyncWebClient,
        channel: str,
        users: List[str],
    ) -> bool:
        """Invite users to a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID
            users: List of user IDs to invite

        Returns:
            True if successful

        Required scopes: channels:manage, groups:write (for private)
        """
        try:
            await client.conversations_invite(
                channel=channel,
                users=",".join(users),
            )
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_leave_channel(
        client: AsyncWebClient,
        channel: str,
    ) -> bool:
        """Leave a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID to leave

        Returns:
            True if successful

        Required scopes: channels:manage, groups:write (for private)
        """
        try:
            await client.conversations_leave(channel=channel)
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_channel_members(
        client: AsyncWebClient,
        channel: str,
        limit: int = 100,
    ) -> List[str]:
        """Get list of members in a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID
            limit: Maximum number of members to return (default: 100)

        Returns:
            List of user IDs

        Required scopes: channels:read, groups:read (for private)
        """
        try:
            response = await client.conversations_members(
                channel=channel,
                limit=limit,
            )
            return response.get("members", [])
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # User Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_list_users(
        client: AsyncWebClient,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List users in the workspace.

        Args:
            client: Slack client (from slack_create_client)
            limit: Maximum number of users to return (default: 100)

        Returns:
            List of user dicts with: id, name, real_name, email, is_bot, is_admin

        Required scopes: users:read, users:read.email (for email)
        """
        try:
            response = await client.users_list(limit=limit)
            users = []
            for user in response.get("members", []):
                users.append(
                    {
                        "id": user["id"],
                        "name": user.get("name", ""),
                        "real_name": user.get("real_name", ""),
                        "email": user.get("profile", {}).get("email", ""),
                        "is_bot": user.get("is_bot", False),
                        "is_admin": user.get("is_admin", False),
                    }
                )
            return users
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_user_info(
        client: AsyncWebClient,
        user: str,
    ) -> Dict[str, Any]:
        """Get information about a user.

        Args:
            client: Slack client (from slack_create_client)
            user: User ID

        Returns:
            Dict with: id, name, real_name, email, title, phone, is_bot, is_admin, tz

        Required scopes: users:read, users:read.email (for email)
        """
        try:
            response = await client.users_info(user=user)
            u = response["user"]
            profile = u.get("profile", {})
            return {
                "id": u["id"],
                "name": u.get("name", ""),
                "real_name": u.get("real_name", ""),
                "email": profile.get("email", ""),
                "title": profile.get("title", ""),
                "phone": profile.get("phone", ""),
                "is_bot": u.get("is_bot", False),
                "is_admin": u.get("is_admin", False),
                "tz": u.get("tz", ""),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_user_presence(
        client: AsyncWebClient,
        user: str,
    ) -> Dict[str, Any]:
        """Get user's presence status.

        Args:
            client: Slack client (from slack_create_client)
            user: User ID

        Returns:
            Dict with: presence (active/away), online, auto_away, manual_away

        Required scopes: users:read
        """
        try:
            response = await client.users_getPresence(user=user)
            return {
                "presence": response.get("presence", ""),
                "online": response.get("online", False),
                "auto_away": response.get("auto_away", False),
                "manual_away": response.get("manual_away", False),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # File Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_upload_file(
        client: AsyncWebClient,
        channels: List[str],
        content: str,
        filename: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a file to channels.

        Args:
            client: Slack client (from slack_create_client)
            channels: List of channel IDs to share the file
            content: File content as string
            filename: Name of the file
            title: Optional title for the file
            initial_comment: Optional comment to add with the file

        Returns:
            Dict with: id, name, title, url_private, permalink

        Required scopes: files:write
        """
        try:
            response = await client.files_upload_v2(
                channels=",".join(channels),
                content=content,
                filename=filename,
                title=title,
                initial_comment=initial_comment,
            )
            file_info = response.get("file", {})
            return {
                "id": file_info.get("id", ""),
                "name": file_info.get("name", ""),
                "title": file_info.get("title", ""),
                "url_private": file_info.get("url_private", ""),
                "permalink": file_info.get("permalink", ""),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_list_files(
        client: AsyncWebClient,
        channel: Optional[str] = None,
        user: Optional[str] = None,
        types: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List files in the workspace.

        Args:
            client: Slack client (from slack_create_client)
            channel: Optional channel ID to filter by
            user: Optional user ID to filter by
            types: Optional comma-separated file types (spaces, snippets, images, etc.)
            limit: Number of files to return (default: 100)

        Returns:
            List of file dicts with: id, name, title, filetype, size, user, created

        Required scopes: files:read
        """
        try:
            kwargs = {"count": limit}
            if channel:
                kwargs["channel"] = channel
            if user:
                kwargs["user"] = user
            if types:
                kwargs["types"] = types

            response = await client.files_list(**kwargs)
            files = []
            for f in response.get("files", []):
                files.append(
                    {
                        "id": f["id"],
                        "name": f.get("name", ""),
                        "title": f.get("title", ""),
                        "filetype": f.get("filetype", ""),
                        "size": f.get("size", 0),
                        "user": f.get("user", ""),
                        "created": f.get("created", 0),
                    }
                )
            return files
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_delete_file(
        client: AsyncWebClient,
        file_id: str,
    ) -> bool:
        """Delete a file.

        Args:
            client: Slack client (from slack_create_client)
            file_id: File ID to delete

        Returns:
            True if successful

        Required scopes: files:write
        """
        try:
            await client.files_delete(file=file_id)
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # Reaction Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_add_reaction(
        client: AsyncWebClient,
        channel: str,
        ts: str,
        emoji: str,
    ) -> bool:
        """Add a reaction emoji to a message.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the message exists
            ts: Timestamp of the message
            emoji: Emoji name without colons (e.g., "thumbsup")

        Returns:
            True if successful

        Required scopes: reactions:write
        """
        try:
            await client.reactions_add(channel=channel, timestamp=ts, name=emoji)
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_remove_reaction(
        client: AsyncWebClient,
        channel: str,
        ts: str,
        emoji: str,
    ) -> bool:
        """Remove a reaction emoji from a message.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the message exists
            ts: Timestamp of the message
            emoji: Emoji name without colons (e.g., "thumbsup")

        Returns:
            True if successful

        Required scopes: reactions:write
        """
        try:
            await client.reactions_remove(channel=channel, timestamp=ts, name=emoji)
            return True
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_reactions(
        client: AsyncWebClient,
        channel: str,
        ts: str,
    ) -> List[Dict[str, Any]]:
        """Get reactions on a message.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the message exists
            ts: Timestamp of the message

        Returns:
            List of reaction dicts with: name, count, users

        Required scopes: reactions:read
        """
        try:
            response = await client.reactions_get(channel=channel, timestamp=ts)
            message = response.get("message", {})
            reactions = []
            for r in message.get("reactions", []):
                reactions.append(
                    {
                        "name": r.get("name", ""),
                        "count": r.get("count", 0),
                        "users": r.get("users", []),
                    }
                )
            return reactions
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # Conversation History
    # =========================================================================

    @opcode(category="slack")
    async def slack_get_conversation_history(
        client: AsyncWebClient,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a channel.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID
            limit: Number of messages to return (default: 100)
            oldest: Optional oldest message timestamp to fetch from
            latest: Optional latest message timestamp to fetch to

        Returns:
            List of message dicts with: ts, text, user, thread_ts, reply_count

        Required scopes: channels:history, groups:history (for private), mpim:history, im:history
        """
        try:
            kwargs = {"channel": channel, "limit": limit}
            if oldest:
                kwargs["oldest"] = oldest
            if latest:
                kwargs["latest"] = latest

            response = await client.conversations_history(**kwargs)
            messages = []
            for msg in response.get("messages", []):
                messages.append(
                    {
                        "ts": msg.get("ts", ""),
                        "text": msg.get("text", ""),
                        "user": msg.get("user", ""),
                        "thread_ts": msg.get("thread_ts"),
                        "reply_count": msg.get("reply_count", 0),
                    }
                )
            return messages
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    @opcode(category="slack")
    async def slack_get_thread_replies(
        client: AsyncWebClient,
        channel: str,
        thread_ts: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get replies in a thread.

        Args:
            client: Slack client (from slack_create_client)
            channel: Channel ID where the thread exists
            thread_ts: Timestamp of the parent message
            limit: Number of replies to return (default: 100)

        Returns:
            List of message dicts with: ts, text, user, thread_ts

        Required scopes: channels:history, groups:history (for private)
        """
        try:
            response = await client.conversations_replies(
                channel=channel,
                ts=thread_ts,
                limit=limit,
            )
            messages = []
            for msg in response.get("messages", []):
                messages.append(
                    {
                        "ts": msg.get("ts", ""),
                        "text": msg.get("text", ""),
                        "user": msg.get("user", ""),
                        "thread_ts": msg.get("thread_ts"),
                    }
                )
            return messages
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")

    # =========================================================================
    # Utility Operations
    # =========================================================================

    @opcode(category="slack")
    async def slack_format_user_mention(user_id: str) -> str:
        """Format a user ID as a mention.

        Args:
            user_id: User ID (e.g., "U12345678")

        Returns:
            Formatted mention string (e.g., "<@U12345678>")
        """
        return f"<@{user_id}>"

    @opcode(category="slack")
    async def slack_format_channel_mention(channel_id: str) -> str:
        """Format a channel ID as a mention.

        Args:
            channel_id: Channel ID (e.g., "C12345678")

        Returns:
            Formatted mention string (e.g., "<#C12345678>")
        """
        return f"<#{channel_id}>"

    @opcode(category="slack")
    async def slack_format_link(url: str, text: Optional[str] = None) -> str:
        """Format a URL as a Slack link.

        Args:
            url: URL to link to
            text: Optional display text

        Returns:
            Formatted link string (e.g., "<https://example.com|Click here>")
        """
        if text:
            return f"<{url}|{text}>"
        return f"<{url}>"

    @opcode(category="slack")
    async def slack_test_auth(
        client: AsyncWebClient,
    ) -> Dict[str, Any]:
        """Test authentication and get bot/user info.

        Args:
            client: Slack client (from slack_create_client)

        Returns:
            Dict with: ok, url, team, user, team_id, user_id, bot_id

        Useful for verifying token validity and getting workspace info.
        """
        try:
            response = await client.auth_test()
            return {
                "ok": response["ok"],
                "url": response.get("url", ""),
                "team": response.get("team", ""),
                "user": response.get("user", ""),
                "team_id": response.get("team_id", ""),
                "user_id": response.get("user_id", ""),
                "bot_id": response.get("bot_id"),
            }
        except SlackApiError as e:
            raise RuntimeError(f"Slack API error: {e.response.get('error', str(e))}")
