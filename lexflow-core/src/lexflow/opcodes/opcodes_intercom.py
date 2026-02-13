"""Intercom opcodes for LexFlow.

This module provides opcodes for interacting with Intercom's REST API,
enabling customer communication and support automation workflows.

Authentication:
    Requires an Intercom Access Token:
    - Go to Settings > Developers > Developer Hub in Intercom
    - Create a new app or use an existing one
    - Generate an Access Token with required permissions

API Reference:
    https://developers.intercom.com/docs/references/rest-api/api.intercom.io/
"""

from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class IntercomClient:
    """Simple Intercom API client."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.intercom.io"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Intercom-Version": "2.11",
        }


def register_intercom_opcodes():
    """Register Intercom opcodes to the default registry."""
    if not AIOHTTP_AVAILABLE:
        return

    register_category(
        id="intercom",
        label="Intercom",
        prefix="intercom_",
        color="#1F8CEB",
        icon="💬",
        order=285,
    )

    # =========================================================================
    # Helper Functions
    # =========================================================================

    async def _request(
        client: IntercomClient,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Intercom API."""
        url = f"{client.base_url}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=client.headers,
                json=json_data,
                params=params,
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"Intercom API error ({response.status}): {error_text}"
                    )
                if response.status == 204:
                    return {}
                return await response.json()

    # =========================================================================
    # Client Management
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_create_client(token: str) -> IntercomClient:
        """Create an Intercom API client.

        Args:
            token: Intercom Access Token

        Returns:
            IntercomClient instance for use with other Intercom opcodes
        """
        return IntercomClient(token=token)

    # =========================================================================
    # Contact Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_create_contact(
        client: IntercomClient,
        role: str,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        external_id: Optional[str] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a contact (user or lead).

        Args:
            client: Intercom client (from intercom_create_client)
            role: Contact role ("user" or "lead")
            email: Contact email address
            name: Contact name
            phone: Contact phone number
            external_id: External ID for the contact
            custom_attributes: Custom attributes dictionary

        Returns:
            Dict with: id, type, role, email, name, phone, external_id, created_at
        """
        data = {"role": role, "email": email}
        if name:
            data["name"] = name
        if phone:
            data["phone"] = phone
        if external_id:
            data["external_id"] = external_id
        if custom_attributes:
            data["custom_attributes"] = custom_attributes

        response = await _request(client, "POST", "/contacts", json_data=data)
        return {
            "id": response.get("id", ""),
            "type": response.get("type", ""),
            "role": response.get("role", ""),
            "email": response.get("email", ""),
            "name": response.get("name", ""),
            "phone": response.get("phone", ""),
            "external_id": response.get("external_id", ""),
            "created_at": response.get("created_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_get_contact(
        client: IntercomClient,
        id: str,
    ) -> Dict[str, Any]:
        """Get a contact by ID.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Contact ID

        Returns:
            Dict with: id, type, role, email, name, phone, external_id, created_at, updated_at
        """
        response = await _request(client, "GET", f"/contacts/{id}")
        return {
            "id": response.get("id", ""),
            "type": response.get("type", ""),
            "role": response.get("role", ""),
            "email": response.get("email", ""),
            "name": response.get("name", ""),
            "phone": response.get("phone", ""),
            "external_id": response.get("external_id", ""),
            "created_at": response.get("created_at", 0),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_update_contact(
        client: IntercomClient,
        id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        external_id: Optional[str] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Contact ID
            email: New email address
            name: New name
            phone: New phone number
            external_id: New external ID
            custom_attributes: Custom attributes to update

        Returns:
            Dict with: id, type, role, email, name, phone, external_id, updated_at
        """
        data = {}
        if email:
            data["email"] = email
        if name:
            data["name"] = name
        if phone:
            data["phone"] = phone
        if external_id:
            data["external_id"] = external_id
        if custom_attributes:
            data["custom_attributes"] = custom_attributes

        response = await _request(client, "PUT", f"/contacts/{id}", json_data=data)
        return {
            "id": response.get("id", ""),
            "type": response.get("type", ""),
            "role": response.get("role", ""),
            "email": response.get("email", ""),
            "name": response.get("name", ""),
            "phone": response.get("phone", ""),
            "external_id": response.get("external_id", ""),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_delete_contact(
        client: IntercomClient,
        id: str,
    ) -> Dict[str, Any]:
        """Delete a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Contact ID to delete

        Returns:
            Dict with: id, type, deleted (boolean)
        """
        response = await _request(client, "DELETE", f"/contacts/{id}")
        return {
            "id": response.get("id", ""),
            "type": response.get("type", ""),
            "deleted": response.get("deleted", True),
        }

    @opcode(category="intercom")
    async def intercom_list_contacts(
        client: IntercomClient,
        per_page: int = 50,
        starting_after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List contacts with pagination.

        Args:
            client: Intercom client (from intercom_create_client)
            per_page: Number of contacts per page (max 150)
            starting_after: Cursor for pagination

        Returns:
            Dict with: contacts (list), total_count, has_more, next_cursor
        """
        params = {"per_page": per_page}
        if starting_after:
            params["starting_after"] = starting_after

        response = await _request(client, "GET", "/contacts", params=params)
        contacts = []
        for c in response.get("data", []):
            contacts.append(
                {
                    "id": c.get("id", ""),
                    "role": c.get("role", ""),
                    "email": c.get("email", ""),
                    "name": c.get("name", ""),
                    "external_id": c.get("external_id", ""),
                }
            )

        pages = response.get("pages", {})
        return {
            "contacts": contacts,
            "total_count": response.get("total_count", len(contacts)),
            "has_more": pages.get("next") is not None,
            "next_cursor": pages.get("next", {}).get("starting_after"),
        }

    @opcode(category="intercom")
    async def intercom_search_contacts(
        client: IntercomClient,
        query: Dict[str, Any],
        per_page: int = 50,
        starting_after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search contacts using query.

        Args:
            client: Intercom client (from intercom_create_client)
            query: Search query object (see Intercom API docs)
            per_page: Number of contacts per page (max 150)
            starting_after: Cursor for pagination

        Returns:
            Dict with: contacts (list), total_count, has_more, next_cursor

        Example query:
            {"field": "email", "operator": "=", "value": "user@example.com"}
        """
        data = {"query": query}
        pagination = {"per_page": per_page}
        if starting_after:
            pagination["starting_after"] = starting_after
        data["pagination"] = pagination

        response = await _request(client, "POST", "/contacts/search", json_data=data)
        contacts = []
        for c in response.get("data", []):
            contacts.append(
                {
                    "id": c.get("id", ""),
                    "role": c.get("role", ""),
                    "email": c.get("email", ""),
                    "name": c.get("name", ""),
                    "external_id": c.get("external_id", ""),
                }
            )

        pages = response.get("pages", {})
        return {
            "contacts": contacts,
            "total_count": response.get("total_count", len(contacts)),
            "has_more": pages.get("next") is not None,
            "next_cursor": pages.get("next", {}).get("starting_after"),
        }

    # =========================================================================
    # Conversation Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_list_conversations(
        client: IntercomClient,
        per_page: int = 20,
        starting_after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List conversations with pagination.

        Args:
            client: Intercom client (from intercom_create_client)
            per_page: Number of conversations per page (max 150)
            starting_after: Cursor for pagination

        Returns:
            Dict with: conversations (list), has_more, next_cursor
        """
        params = {"per_page": per_page}
        if starting_after:
            params["starting_after"] = starting_after

        response = await _request(client, "GET", "/conversations", params=params)
        conversations = []
        for conv in response.get("conversations", []):
            conversations.append(
                {
                    "id": conv.get("id", ""),
                    "state": conv.get("state", ""),
                    "open": conv.get("open", False),
                    "read": conv.get("read", False),
                    "priority": conv.get("priority", ""),
                    "created_at": conv.get("created_at", 0),
                    "updated_at": conv.get("updated_at", 0),
                }
            )

        pages = response.get("pages", {})
        return {
            "conversations": conversations,
            "has_more": pages.get("next") is not None,
            "next_cursor": pages.get("next", {}).get("starting_after"),
        }

    @opcode(category="intercom")
    async def intercom_get_conversation(
        client: IntercomClient,
        id: str,
    ) -> Dict[str, Any]:
        """Get a conversation by ID.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Conversation ID

        Returns:
            Dict with: id, state, open, read, priority, source, contacts, assignee, created_at, updated_at
        """
        response = await _request(client, "GET", f"/conversations/{id}")

        contacts = []
        for c in response.get("contacts", {}).get("contacts", []):
            contacts.append({"id": c.get("id", ""), "type": c.get("type", "")})

        assignee = response.get("assignee", {})
        return {
            "id": response.get("id", ""),
            "state": response.get("state", ""),
            "open": response.get("open", False),
            "read": response.get("read", False),
            "priority": response.get("priority", ""),
            "source": response.get("source", {}).get("type", ""),
            "contacts": contacts,
            "assignee": {
                "id": assignee.get("id", ""),
                "type": assignee.get("type", ""),
            }
            if assignee
            else None,
            "created_at": response.get("created_at", 0),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_reply_to_conversation(
        client: IntercomClient,
        id: str,
        body: str,
        type: str = "admin",
        admin_id: Optional[str] = None,
        message_type: str = "comment",
    ) -> Dict[str, Any]:
        """Reply to a conversation.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Conversation ID
            body: Reply body text
            type: Reply type ("admin" or "user")
            admin_id: Admin ID (required if type is "admin")
            message_type: Message type ("comment" or "note")

        Returns:
            Dict with: type, id, conversation_id, body, created_at
        """
        data = {"body": body, "message_type": message_type, "type": type}
        if type == "admin" and admin_id:
            data["admin_id"] = admin_id

        response = await _request(
            client, "POST", f"/conversations/{id}/reply", json_data=data
        )
        return {
            "type": response.get("type", ""),
            "id": response.get("id", ""),
            "conversation_id": id,
            "body": response.get("body", ""),
            "created_at": response.get("created_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_close_conversation(
        client: IntercomClient,
        id: str,
        admin_id: str,
        body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Close a conversation.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Conversation ID
            admin_id: Admin ID performing the action
            body: Optional closing message

        Returns:
            Dict with: id, state, open, updated_at
        """
        data = {"type": "admin", "admin_id": admin_id, "message_type": "close"}
        if body:
            data["body"] = body

        response = await _request(
            client, "POST", f"/conversations/{id}/parts", json_data=data
        )
        return {
            "id": response.get("id", id),
            "state": response.get("state", "closed"),
            "open": response.get("open", False),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_assign_conversation(
        client: IntercomClient,
        id: str,
        admin_id: str,
        assignee_id: str,
        body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assign a conversation to an admin or team.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Conversation ID
            admin_id: Admin ID performing the assignment
            assignee_id: Admin or team ID to assign to
            body: Optional message about the assignment

        Returns:
            Dict with: id, assignee_id, assignee_type, updated_at
        """
        data = {
            "type": "admin",
            "admin_id": admin_id,
            "assignee_id": assignee_id,
            "message_type": "assignment",
        }
        if body:
            data["body"] = body

        response = await _request(
            client, "POST", f"/conversations/{id}/parts", json_data=data
        )
        assignee = response.get("assignee", {})
        return {
            "id": response.get("id", id),
            "assignee_id": assignee.get("id", assignee_id),
            "assignee_type": assignee.get("type", ""),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_snooze_conversation(
        client: IntercomClient,
        id: str,
        admin_id: str,
        snoozed_until: int,
    ) -> Dict[str, Any]:
        """Snooze a conversation until a specific time.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Conversation ID
            admin_id: Admin ID performing the action
            snoozed_until: Unix timestamp for when to unsnooze

        Returns:
            Dict with: id, state, snoozed_until, updated_at
        """
        data = {
            "type": "admin",
            "admin_id": admin_id,
            "message_type": "snoozed",
            "snoozed_until": snoozed_until,
        }

        response = await _request(
            client, "POST", f"/conversations/{id}/parts", json_data=data
        )
        return {
            "id": response.get("id", id),
            "state": response.get("state", "snoozed"),
            "snoozed_until": response.get("snoozed_until", snoozed_until),
            "updated_at": response.get("updated_at", 0),
        }

    # =========================================================================
    # Message Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_send_message(
        client: IntercomClient,
        from_admin_id: str,
        to_contact_id: str,
        body: str,
        message_type: str = "inapp",
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message to a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            from_admin_id: Admin ID sending the message
            to_contact_id: Contact ID to send to
            body: Message body
            message_type: Message type ("inapp" or "email")
            subject: Email subject (required for email type)

        Returns:
            Dict with: type, id, body, message_type, created_at
        """
        data = {
            "message_type": message_type,
            "body": body,
            "from": {"type": "admin", "id": from_admin_id},
            "to": {"type": "contact", "id": to_contact_id},
        }
        if message_type == "email" and subject:
            data["subject"] = subject

        response = await _request(client, "POST", "/messages", json_data=data)
        return {
            "type": response.get("type", ""),
            "id": response.get("id", ""),
            "body": response.get("body", ""),
            "message_type": response.get("message_type", message_type),
            "created_at": response.get("created_at", 0),
        }

    # =========================================================================
    # Company Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_create_company(
        client: IntercomClient,
        company_id: str,
        name: str,
        plan: Optional[str] = None,
        monthly_spend: Optional[float] = None,
        website: Optional[str] = None,
        industry: Optional[str] = None,
        size: Optional[int] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create or update a company.

        Args:
            client: Intercom client (from intercom_create_client)
            company_id: Unique company ID (external identifier)
            name: Company name
            plan: Company plan name
            monthly_spend: Monthly spend amount
            website: Company website URL
            industry: Industry name
            size: Company size (number of employees)
            custom_attributes: Custom attributes dictionary

        Returns:
            Dict with: id, company_id, name, plan, monthly_spend, created_at, updated_at
        """
        data = {"company_id": company_id, "name": name}
        if plan:
            data["plan"] = plan
        if monthly_spend is not None:
            data["monthly_spend"] = monthly_spend
        if website:
            data["website"] = website
        if industry:
            data["industry"] = industry
        if size is not None:
            data["size"] = size
        if custom_attributes:
            data["custom_attributes"] = custom_attributes

        response = await _request(client, "POST", "/companies", json_data=data)
        return {
            "id": response.get("id", ""),
            "company_id": response.get("company_id", company_id),
            "name": response.get("name", name),
            "plan": response.get("plan", {}).get("name", ""),
            "monthly_spend": response.get("monthly_spend", 0),
            "created_at": response.get("created_at", 0),
            "updated_at": response.get("updated_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_get_company(
        client: IntercomClient,
        id: str,
    ) -> Dict[str, Any]:
        """Get a company by ID.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Company ID (Intercom internal ID)

        Returns:
            Dict with: id, company_id, name, plan, monthly_spend, website, industry, size, user_count, created_at
        """
        response = await _request(client, "GET", f"/companies/{id}")
        return {
            "id": response.get("id", ""),
            "company_id": response.get("company_id", ""),
            "name": response.get("name", ""),
            "plan": response.get("plan", {}).get("name", ""),
            "monthly_spend": response.get("monthly_spend", 0),
            "website": response.get("website", ""),
            "industry": response.get("industry", ""),
            "size": response.get("size", 0),
            "user_count": response.get("user_count", 0),
            "created_at": response.get("created_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_list_companies(
        client: IntercomClient,
        per_page: int = 50,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List companies with pagination.

        Args:
            client: Intercom client (from intercom_create_client)
            per_page: Number of companies per page (max 60)
            page: Page number

        Returns:
            Dict with: companies (list), total_count, page, pages
        """
        params = {"per_page": per_page, "page": page}

        response = await _request(client, "GET", "/companies", params=params)
        companies = []
        for c in response.get("data", []):
            companies.append(
                {
                    "id": c.get("id", ""),
                    "company_id": c.get("company_id", ""),
                    "name": c.get("name", ""),
                    "plan": c.get("plan", {}).get("name", ""),
                    "user_count": c.get("user_count", 0),
                }
            )

        pages_info = response.get("pages", {})
        return {
            "companies": companies,
            "total_count": response.get("total_count", len(companies)),
            "page": pages_info.get("page", page),
            "pages": pages_info.get("total_pages", 1),
        }

    # =========================================================================
    # Tag Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_create_tag(
        client: IntercomClient,
        name: str,
    ) -> Dict[str, Any]:
        """Create a tag.

        Args:
            client: Intercom client (from intercom_create_client)
            name: Tag name

        Returns:
            Dict with: type, id, name
        """
        response = await _request(client, "POST", "/tags", json_data={"name": name})
        return {
            "type": response.get("type", "tag"),
            "id": response.get("id", ""),
            "name": response.get("name", name),
        }

    @opcode(category="intercom")
    async def intercom_list_tags(
        client: IntercomClient,
    ) -> List[Dict[str, Any]]:
        """List all tags.

        Args:
            client: Intercom client (from intercom_create_client)

        Returns:
            List of tag dicts with: type, id, name
        """
        response = await _request(client, "GET", "/tags")
        tags = []
        for t in response.get("data", []):
            tags.append(
                {
                    "type": t.get("type", "tag"),
                    "id": t.get("id", ""),
                    "name": t.get("name", ""),
                }
            )
        return tags

    @opcode(category="intercom")
    async def intercom_tag_contact(
        client: IntercomClient,
        contact_id: str,
        tag_id: str,
    ) -> Dict[str, Any]:
        """Add a tag to a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            contact_id: Contact ID
            tag_id: Tag ID

        Returns:
            Dict with: type, id, name
        """
        response = await _request(
            client, "POST", f"/contacts/{contact_id}/tags", json_data={"id": tag_id}
        )
        return {
            "type": response.get("type", "tag"),
            "id": response.get("id", tag_id),
            "name": response.get("name", ""),
        }

    @opcode(category="intercom")
    async def intercom_untag_contact(
        client: IntercomClient,
        contact_id: str,
        tag_id: str,
    ) -> Dict[str, Any]:
        """Remove a tag from a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            contact_id: Contact ID
            tag_id: Tag ID

        Returns:
            Dict with: type, id, name
        """
        response = await _request(
            client, "DELETE", f"/contacts/{contact_id}/tags/{tag_id}"
        )
        return {
            "type": response.get("type", "tag"),
            "id": response.get("id", tag_id),
            "name": response.get("name", ""),
        }

    # =========================================================================
    # Note Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_create_note(
        client: IntercomClient,
        contact_id: str,
        body: str,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a note on a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            contact_id: Contact ID
            body: Note body text
            admin_id: Admin ID who creates the note

        Returns:
            Dict with: type, id, body, author, created_at
        """
        data = {"body": body}
        if admin_id:
            data["admin_id"] = admin_id

        response = await _request(
            client, "POST", f"/contacts/{contact_id}/notes", json_data=data
        )
        author = response.get("author", {})
        return {
            "type": response.get("type", "note"),
            "id": response.get("id", ""),
            "body": response.get("body", body),
            "author": {
                "type": author.get("type", ""),
                "id": author.get("id", ""),
                "name": author.get("name", ""),
            }
            if author
            else None,
            "created_at": response.get("created_at", 0),
        }

    @opcode(category="intercom")
    async def intercom_list_notes(
        client: IntercomClient,
        contact_id: str,
        per_page: int = 50,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List notes for a contact.

        Args:
            client: Intercom client (from intercom_create_client)
            contact_id: Contact ID
            per_page: Number of notes per page
            page: Page number

        Returns:
            Dict with: notes (list), total_count, page, pages
        """
        params = {"per_page": per_page, "page": page}

        response = await _request(
            client, "GET", f"/contacts/{contact_id}/notes", params=params
        )
        notes = []
        for n in response.get("data", []):
            author = n.get("author", {})
            notes.append(
                {
                    "id": n.get("id", ""),
                    "body": n.get("body", ""),
                    "author": {
                        "type": author.get("type", ""),
                        "id": author.get("id", ""),
                        "name": author.get("name", ""),
                    }
                    if author
                    else None,
                    "created_at": n.get("created_at", 0),
                }
            )

        pages_info = response.get("pages", {})
        return {
            "notes": notes,
            "total_count": response.get("total_count", len(notes)),
            "page": pages_info.get("page", page),
            "pages": pages_info.get("total_pages", 1),
        }

    # =========================================================================
    # Admin Operations
    # =========================================================================

    @opcode(category="intercom")
    async def intercom_list_admins(
        client: IntercomClient,
    ) -> List[Dict[str, Any]]:
        """List all admins/teammates.

        Args:
            client: Intercom client (from intercom_create_client)

        Returns:
            List of admin dicts with: type, id, name, email, job_title, away_mode_enabled
        """
        response = await _request(client, "GET", "/admins")
        admins = []
        for a in response.get("admins", []):
            admins.append(
                {
                    "type": a.get("type", "admin"),
                    "id": a.get("id", ""),
                    "name": a.get("name", ""),
                    "email": a.get("email", ""),
                    "job_title": a.get("job_title", ""),
                    "away_mode_enabled": a.get("away_mode_enabled", False),
                }
            )
        return admins

    @opcode(category="intercom")
    async def intercom_get_admin(
        client: IntercomClient,
        id: str,
    ) -> Dict[str, Any]:
        """Get admin details.

        Args:
            client: Intercom client (from intercom_create_client)
            id: Admin ID

        Returns:
            Dict with: type, id, name, email, job_title, away_mode_enabled, has_inbox_seat
        """
        response = await _request(client, "GET", f"/admins/{id}")
        return {
            "type": response.get("type", "admin"),
            "id": response.get("id", ""),
            "name": response.get("name", ""),
            "email": response.get("email", ""),
            "job_title": response.get("job_title", ""),
            "away_mode_enabled": response.get("away_mode_enabled", False),
            "has_inbox_seat": response.get("has_inbox_seat", False),
        }
