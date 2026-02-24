"""Tests for Slack opcodes."""

import importlib.util

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lexflow import default_registry

pytestmark = pytest.mark.asyncio

SLACK_SDK_AVAILABLE = importlib.util.find_spec("slack_sdk") is not None


def make_slack_error(error_text="test_error"):
    """Create a mock SlackApiError."""
    from slack_sdk.errors import SlackApiError

    resp = MagicMock()
    resp.get.return_value = error_text
    err = SlackApiError(message="error", response=resp)
    return err


def mock_client():
    """Create a mock AsyncWebClient."""
    return AsyncMock()


# =========================================================================
# Graceful degradation (L1)
# =========================================================================


@pytest.mark.skipif(
    SLACK_SDK_AVAILABLE, reason="Test only when slack_sdk is NOT installed"
)
class TestSlackOpcodesNotAvailable:
    async def test_slack_opcodes_not_registered_when_not_installed(self):
        slack_opcodes = [
            name
            for name in default_registry.list_opcodes()
            if name.startswith("slack_") and name != "slack_send_webhook"
        ]
        assert len(slack_opcodes) == 0

    async def test_slack_send_webhook_still_registered(self):
        assert "slack_send_webhook" in default_registry.list_opcodes()


# =========================================================================
# Client Management
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackCreateClient:
    async def test_create_client_returns_async_web_client(self):
        with patch("lexflow.opcodes.opcodes_slack.AsyncWebClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            result = await default_registry.call("slack_create_client", ["xoxb-test"])
            mock_cls.assert_called_once_with(token="xoxb-test")
            assert result is mock_cls.return_value


# =========================================================================
# Message Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackMessages:
    async def test_send_message(self):
        client = mock_client()
        client.chat_postMessage.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.5678",
            "message": {"text": "hello"},
        }
        result = await default_registry.call(
            "slack_send_message", [client, "C123", "hello"]
        )
        assert result["ok"] is True
        assert result["channel"] == "C123"
        assert result["ts"] == "1234.5678"
        client.chat_postMessage.assert_called_once()

    async def test_send_message_in_thread(self):
        client = mock_client()
        client.chat_postMessage.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.9999",
            "message": {},
        }
        result = await default_registry.call(
            "slack_send_message", [client, "C123", "reply", "1234.5678"]
        )
        assert result["ok"] is True
        kwargs = client.chat_postMessage.call_args[1]
        assert kwargs["thread_ts"] == "1234.5678"

    async def test_send_message_error(self):
        client = mock_client()
        client.chat_postMessage.side_effect = make_slack_error("channel_not_found")
        with pytest.raises(RuntimeError, match="channel_not_found"):
            await default_registry.call("slack_send_message", [client, "C123", "hi"])

    async def test_send_blocks(self):
        client = mock_client()
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "hello"}}]
        client.chat_postMessage.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.5678",
            "message": {},
        }
        result = await default_registry.call(
            "slack_send_blocks", [client, "C123", blocks, "fallback"]
        )
        assert result["ok"] is True
        kwargs = client.chat_postMessage.call_args[1]
        assert kwargs["blocks"] == blocks

    async def test_update_message(self):
        client = mock_client()
        client.chat_update.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.5678",
            "message": {"text": "updated"},
        }
        result = await default_registry.call(
            "slack_update_message", [client, "C123", "1234.5678", "updated"]
        )
        assert result["ok"] is True
        client.chat_update.assert_called_once()

    async def test_update_message_error(self):
        client = mock_client()
        client.chat_update.side_effect = make_slack_error("message_not_found")
        with pytest.raises(RuntimeError, match="message_not_found"):
            await default_registry.call(
                "slack_update_message", [client, "C123", "1234.5678", "text"]
            )

    async def test_delete_message(self):
        client = mock_client()
        client.chat_delete.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.5678",
        }
        result = await default_registry.call(
            "slack_delete_message", [client, "C123", "1234.5678"]
        )
        assert result["ok"] is True
        client.chat_delete.assert_called_once_with(channel="C123", ts="1234.5678")

    async def test_schedule_message(self):
        client = mock_client()
        client.chat_scheduleMessage.return_value = {
            "ok": True,
            "channel": "C123",
            "scheduled_message_id": "Q123",
            "post_at": 1700000000,
        }
        result = await default_registry.call(
            "slack_schedule_message", [client, "C123", "later", 1700000000]
        )
        assert result["ok"] is True
        assert result["scheduled_message_id"] == "Q123"

    async def test_reply_in_thread_with_broadcast(self):
        client = mock_client()
        client.chat_postMessage.return_value = {
            "ok": True,
            "channel": "C123",
            "ts": "1234.9999",
            "message": {},
        }
        await default_registry.call(
            "slack_send_message",
            [client, "C123", "broadcast reply", "1234.5678", True],
        )
        kwargs = client.chat_postMessage.call_args[1]
        assert kwargs["reply_broadcast"] is True


# =========================================================================
# Channel Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackChannels:
    async def test_list_channels(self):
        client = mock_client()
        client.conversations_list.return_value = {
            "channels": [
                {
                    "id": "C1",
                    "name": "general",
                    "is_private": False,
                    "is_archived": False,
                    "num_members": 10,
                },
            ]
        }
        result = await default_registry.call("slack_list_channels", [client])
        assert len(result) == 1
        assert result[0]["id"] == "C1"
        assert result[0]["name"] == "general"

    async def test_list_channels_error(self):
        client = mock_client()
        client.conversations_list.side_effect = make_slack_error("invalid_auth")
        with pytest.raises(RuntimeError, match="invalid_auth"):
            await default_registry.call("slack_list_channels", [client])

    async def test_create_channel(self):
        client = mock_client()
        client.conversations_create.return_value = {
            "channel": {
                "id": "C999",
                "name": "new-channel",
                "is_private": False,
                "created": 1700000000,
            }
        }
        result = await default_registry.call(
            "slack_create_channel", [client, "new-channel"]
        )
        assert result["id"] == "C999"
        assert result["name"] == "new-channel"

    async def test_archive_channel(self):
        client = mock_client()
        client.conversations_archive.return_value = {"ok": True}
        result = await default_registry.call("slack_archive_channel", [client, "C123"])
        assert result is True

    async def test_get_channel_info(self):
        client = mock_client()
        client.conversations_info.return_value = {
            "channel": {
                "id": "C123",
                "name": "general",
                "is_private": False,
                "is_archived": False,
                "topic": {"value": "General chat"},
                "purpose": {"value": "Company-wide"},
                "num_members": 50,
                "created": 1600000000,
            }
        }
        result = await default_registry.call("slack_get_channel_info", [client, "C123"])
        assert result["id"] == "C123"
        assert result["topic"] == "General chat"
        assert result["purpose"] == "Company-wide"

    async def test_invite_to_channel(self):
        client = mock_client()
        client.conversations_invite.return_value = {"ok": True}
        result = await default_registry.call(
            "slack_invite_to_channel", [client, "C123", ["U1", "U2"]]
        )
        assert result is True
        client.conversations_invite.assert_called_once_with(
            channel="C123", users="U1,U2"
        )

    async def test_leave_channel(self):
        client = mock_client()
        client.conversations_leave.return_value = {"ok": True}
        result = await default_registry.call("slack_leave_channel", [client, "C123"])
        assert result is True

    async def test_get_channel_members(self):
        client = mock_client()
        client.conversations_members.return_value = {"members": ["U1", "U2", "U3"]}
        result = await default_registry.call(
            "slack_get_channel_members", [client, "C123"]
        )
        assert result == ["U1", "U2", "U3"]


# =========================================================================
# User Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackUsers:
    async def test_list_users(self):
        client = mock_client()
        client.users_list.return_value = {
            "members": [
                {
                    "id": "U1",
                    "name": "alice",
                    "real_name": "Alice",
                    "profile": {"email": "alice@test.com"},
                    "is_bot": False,
                    "is_admin": True,
                },
            ]
        }
        result = await default_registry.call("slack_list_users", [client])
        assert len(result) == 1
        assert result[0]["id"] == "U1"
        assert result[0]["email"] == "alice@test.com"
        assert result[0]["is_admin"] is True

    async def test_get_user_info(self):
        client = mock_client()
        client.users_info.return_value = {
            "user": {
                "id": "U1",
                "name": "alice",
                "real_name": "Alice",
                "profile": {"email": "a@t.com", "title": "Eng", "phone": "123"},
                "is_bot": False,
                "is_admin": False,
                "tz": "America/New_York",
            }
        }
        result = await default_registry.call("slack_get_user_info", [client, "U1"])
        assert result["id"] == "U1"
        assert result["title"] == "Eng"
        assert result["tz"] == "America/New_York"

    async def test_get_user_presence(self):
        client = mock_client()
        client.users_getPresence.return_value = {
            "presence": "active",
            "online": True,
            "auto_away": False,
            "manual_away": False,
        }
        result = await default_registry.call("slack_get_user_presence", [client, "U1"])
        assert result["presence"] == "active"
        assert result["online"] is True


# =========================================================================
# File Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackFiles:
    async def test_upload_file(self):
        client = mock_client()
        client.files_upload_v2.return_value = {
            "file": {
                "id": "F1",
                "name": "test.txt",
                "title": "Test File",
                "url_private": "https://files.slack.com/test.txt",
                "permalink": "https://team.slack.com/files/test.txt",
            }
        }
        result = await default_registry.call(
            "slack_upload_file", [client, ["C123"], "content", "test.txt"]
        )
        assert result["id"] == "F1"
        assert result["name"] == "test.txt"

    async def test_list_files(self):
        client = mock_client()
        client.files_list.return_value = {
            "files": [
                {
                    "id": "F1",
                    "name": "a.txt",
                    "title": "A",
                    "filetype": "text",
                    "size": 100,
                    "user": "U1",
                    "created": 1700000000,
                },
            ]
        }
        result = await default_registry.call("slack_list_files", [client])
        assert len(result) == 1
        assert result[0]["id"] == "F1"
        assert result[0]["size"] == 100

    async def test_delete_file(self):
        client = mock_client()
        client.files_delete.return_value = {"ok": True}
        result = await default_registry.call("slack_delete_file", [client, "F1"])
        assert result is True
        client.files_delete.assert_called_once_with(file="F1")


# =========================================================================
# Reaction Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackReactions:
    async def test_add_reaction(self):
        client = mock_client()
        client.reactions_add.return_value = {"ok": True}
        result = await default_registry.call(
            "slack_add_reaction", [client, "C123", "1234.5678", "thumbsup"]
        )
        assert result is True
        client.reactions_add.assert_called_once_with(
            channel="C123", timestamp="1234.5678", name="thumbsup"
        )

    async def test_remove_reaction(self):
        client = mock_client()
        client.reactions_remove.return_value = {"ok": True}
        result = await default_registry.call(
            "slack_remove_reaction", [client, "C123", "1234.5678", "thumbsup"]
        )
        assert result is True

    async def test_get_reactions(self):
        client = mock_client()
        client.reactions_get.return_value = {
            "message": {
                "reactions": [
                    {"name": "thumbsup", "count": 3, "users": ["U1", "U2", "U3"]},
                    {"name": "heart", "count": 1, "users": ["U1"]},
                ]
            }
        }
        result = await default_registry.call(
            "slack_get_reactions", [client, "C123", "1234.5678"]
        )
        assert len(result) == 2
        assert result[0]["name"] == "thumbsup"
        assert result[0]["count"] == 3

    async def test_get_reactions_no_reactions(self):
        client = mock_client()
        client.reactions_get.return_value = {"message": {}}
        result = await default_registry.call(
            "slack_get_reactions", [client, "C123", "1234.5678"]
        )
        assert result == []


# =========================================================================
# Conversation History
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackConversations:
    async def test_get_conversation_history(self):
        client = mock_client()
        client.conversations_history.return_value = {
            "messages": [
                {
                    "ts": "1234.5678",
                    "text": "hello",
                    "user": "U1",
                    "thread_ts": None,
                    "reply_count": 0,
                },
            ]
        }
        result = await default_registry.call(
            "slack_get_conversation_history", [client, "C123"]
        )
        assert len(result) == 1
        assert result[0]["text"] == "hello"

    async def test_get_thread_replies(self):
        client = mock_client()
        client.conversations_replies.return_value = {
            "messages": [
                {
                    "ts": "1234.5678",
                    "text": "parent",
                    "user": "U1",
                    "thread_ts": "1234.5678",
                },
                {
                    "ts": "1234.9999",
                    "text": "reply",
                    "user": "U2",
                    "thread_ts": "1234.5678",
                },
            ]
        }
        result = await default_registry.call(
            "slack_get_thread_replies", [client, "C123", "1234.5678"]
        )
        assert len(result) == 2
        assert result[1]["text"] == "reply"


# =========================================================================
# Webhook (no slack_sdk dependency)
# =========================================================================


def _mock_aiohttp_session(response_status=200):
    """Create a mock aiohttp session with proper async context managers."""
    mock_response = MagicMock()
    mock_response.status = response_status

    # session.post() must return an async context manager (not a coroutine)
    post_ctx = MagicMock()
    post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    post_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post.return_value = post_ctx

    # ClientSession() itself is an async context manager
    session_ctx = MagicMock()
    session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    session_ctx.__aexit__ = AsyncMock(return_value=False)

    return session_ctx


class TestSlackWebhook:
    async def test_send_webhook_success(self):
        session_ctx = _mock_aiohttp_session(200)
        with patch("aiohttp.ClientSession", return_value=session_ctx):
            result = await default_registry.call(
                "slack_send_webhook",
                ["https://hooks.slack.com/services/T/B/xxx", "hello"],
            )
            assert result is True

    async def test_send_webhook_rejects_non_https(self):
        with pytest.raises(ValueError, match="must use HTTPS"):
            await default_registry.call(
                "slack_send_webhook",
                ["http://hooks.slack.com/services/T/B/xxx", "hello"],
            )

    async def test_send_webhook_rejects_non_slack_host(self):
        with pytest.raises(ValueError, match="host not allowed"):
            await default_registry.call(
                "slack_send_webhook",
                ["https://evil.com/services/T/B/xxx", "hello"],
            )

    async def test_send_webhook_error_status(self):
        session_ctx = _mock_aiohttp_session(403)
        with patch("aiohttp.ClientSession", return_value=session_ctx):
            with pytest.raises(RuntimeError, match="status 403"):
                await default_registry.call(
                    "slack_send_webhook",
                    ["https://hooks.slack.com/services/T/B/xxx", "hello"],
                )


# =========================================================================
# Utility Operations
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackUtilities:
    async def test_format_user_mention(self):
        result = await default_registry.call("slack_format_user_mention", ["U12345678"])
        assert result == "<@U12345678>"

    async def test_format_channel_mention(self):
        result = await default_registry.call(
            "slack_format_channel_mention", ["C12345678"]
        )
        assert result == "<#C12345678>"

    async def test_format_link_with_text(self):
        result = await default_registry.call(
            "slack_format_link", ["https://example.com", "Click here"]
        )
        assert result == "<https://example.com|Click here>"

    async def test_format_link_without_text(self):
        result = await default_registry.call(
            "slack_format_link", ["https://example.com"]
        )
        assert result == "<https://example.com>"

    async def test_auth(self):
        client = mock_client()
        client.auth_test.return_value = {
            "ok": True,
            "url": "https://team.slack.com",
            "team": "Team",
            "user": "bot",
            "team_id": "T123",
            "user_id": "U123",
            "bot_id": "B123",
        }
        result = await default_registry.call("slack_test_auth", [client])
        assert result["ok"] is True
        assert result["bot_id"] == "B123"


# =========================================================================
# Error Handling
# =========================================================================


@pytest.mark.skipif(not SLACK_SDK_AVAILABLE, reason="slack_sdk not installed")
class TestSlackErrorHandling:
    async def test_send_message_wraps_slack_api_error(self):
        client = mock_client()
        client.chat_postMessage.side_effect = make_slack_error("not_authed")
        with pytest.raises(RuntimeError, match="not_authed"):
            await default_registry.call("slack_send_message", [client, "C1", "hi"])

    async def test_list_channels_wraps_slack_api_error(self):
        client = mock_client()
        client.conversations_list.side_effect = make_slack_error("invalid_auth")
        with pytest.raises(RuntimeError, match="invalid_auth"):
            await default_registry.call("slack_list_channels", [client])

    async def test_upload_file_wraps_slack_api_error(self):
        client = mock_client()
        client.files_upload_v2.side_effect = make_slack_error("file_too_large")
        with pytest.raises(RuntimeError, match="file_too_large"):
            await default_registry.call(
                "slack_upload_file", [client, ["C1"], "data", "f.txt"]
            )

    async def test_auth_test_wraps_slack_api_error(self):
        client = mock_client()
        client.auth_test.side_effect = make_slack_error("token_revoked")
        with pytest.raises(RuntimeError, match="token_revoked"):
            await default_registry.call("slack_test_auth", [client])
