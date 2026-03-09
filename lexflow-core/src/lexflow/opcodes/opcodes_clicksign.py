"""Clicksign digital signing opcodes for LexFlow.

This module provides opcodes for interacting with Clicksign API v3.0,
enabling envelope-based digital signing workflows.

Authentication:
    Clicksign uses plain access tokens (no Bearer prefix). Generate one at:
    https://developers.clicksign.com/docs/api-authentication
"""

from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import aiohttp

    CLICKSIGN_AVAILABLE = True
except ImportError:
    CLICKSIGN_AVAILABLE = False


class ClicksignClient:
    """Reusable Clicksign API client."""

    def __init__(self, access_token: str, sandbox: bool = True):
        base = (
            "https://sandbox.clicksign.com" if sandbox else "https://app.clicksign.com"
        )
        self.base_url = f"{base}/api/v3"
        self.sandbox = sandbox
        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": access_token,
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            },
        )

    def __repr__(self) -> str:
        return f"ClicksignClient(sandbox={self.sandbox})"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Clicksign API."""
        url = f"{self.base_url}{endpoint}"

        async with self._session.request(
            method, url, params=params, json=json_data
        ) as response:
            if response.status == 204:
                return {}

            data = await response.json()

            if response.status >= 400:
                errors = data.get("errors", [])
                if errors:
                    err = errors[0]
                    detail = err.get("detail", "Unknown error")
                    code = err.get("code", "")
                    raise ValueError(
                        f"Clicksign API error ({response.status}): {detail}. Code: {code}"
                    )
                raise ValueError(f"Clicksign API error ({response.status})")

            return data

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", endpoint, json_data=json_data)

    async def patch(
        self, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self._request("PATCH", endpoint, json_data=json_data)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint)


def register_clicksign_opcodes():
    """Register Clicksign opcodes to the default registry."""
    if not CLICKSIGN_AVAILABLE:
        return

    register_category(
        id="clicksign",
        label="Clicksign Operations",
        prefix="clicksign_",
        color="#4B0082",
        icon="clicksign",
        requires="clicksign",
        order=220,
    )

    # ============================================================================
    # Authentication
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_create_client(
        access_token: str,
        sandbox: bool = True,
    ) -> ClicksignClient:
        """Create a Clicksign API client for digital signing operations.

        Args:
            access_token: Clicksign API access token
            sandbox: Use sandbox environment (default: True)

        Returns:
            ClicksignClient object to use with other clicksign_* opcodes

        Example:
            access_token: "your-access-token"
            sandbox: true
        """
        if not access_token:
            raise ValueError(
                "access_token is required. "
                "Generate one at: https://developers.clicksign.com/docs/api-authentication"
            )

        return ClicksignClient(access_token, sandbox=sandbox)

    @opcode(category="clicksign")
    async def clicksign_close_client(client: ClicksignClient) -> bool:
        """Close a Clicksign client and release its resources.

        Args:
            client: ClicksignClient to close

        Returns:
            True when the client session is closed
        """
        await client._session.close()
        return True

    # ============================================================================
    # Envelopes
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_create_envelope(
        client: ClicksignClient,
        name: str,
        locale: str = "pt-BR",
        auto_close: bool = True,
        remind_interval: str = "3",
        block_after_refusal: bool = False,
        deadline_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new signing envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            name: Name of the envelope
            locale: Envelope locale (default: pt-BR)
            auto_close: Auto-close after all signers sign (default: True)
            remind_interval: Reminder interval in days (default: "3")
            block_after_refusal: Block envelope after a signer refuses (default: False)
            deadline_at: Optional deadline in ISO 8601 format

        Returns:
            Created envelope object (JSON:API response)

        Example:
            client: { node: create_client }
            name: "Contract 2024"
            locale: "pt-BR"
            auto_close: true
        """
        attributes: Dict[str, Any] = {
            "name": name,
            "locale": locale,
            "auto_close": auto_close,
            "remind_interval": remind_interval,
            "block_after_refusal": block_after_refusal,
        }
        if deadline_at is not None:
            attributes["deadline_at"] = deadline_at

        body = {"data": {"type": "envelopes", "attributes": attributes}}
        return await client.post("/envelopes", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_get_envelope(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """Get an envelope by ID.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            Envelope object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        return await client.get(f"/envelopes/{envelope_id}")

    @opcode(category="clicksign")
    async def clicksign_list_envelopes(
        client: ClicksignClient,
        status: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List envelopes with optional filters.

        Args:
            client: ClicksignClient from clicksign_create_client
            status: Filter by status (e.g., "running", "closed", "canceled")
            name: Filter by name

        Returns:
            List of envelopes (JSON:API response)

        Example:
            client: { node: create_client }
            status: "running"
        """
        params: Dict[str, str] = {}
        if status is not None:
            params["filter[status]"] = status
        if name is not None:
            params["filter[name]"] = name

        return await client.get("/envelopes", params=params)

    @opcode(category="clicksign")
    async def clicksign_activate_envelope(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """Activate an envelope to start the signing process.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            Updated envelope object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        body = {
            "data": {
                "type": "envelopes",
                "attributes": {"status": "running"},
            }
        }
        return await client.patch(f"/envelopes/{envelope_id}", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_cancel_envelope(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """Cancel an active envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            Updated envelope object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        body = {
            "data": {
                "type": "envelopes",
                "attributes": {"status": "canceled"},
            }
        }
        return await client.patch(f"/envelopes/{envelope_id}", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_delete_envelope(
        client: ClicksignClient,
        envelope_id: str,
    ) -> bool:
        """Delete an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        await client.delete(f"/envelopes/{envelope_id}")
        return True

    # ============================================================================
    # Documents
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_add_document_from_template(
        client: ClicksignClient,
        envelope_id: str,
        template_id: str,
        filename: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a document to an envelope using a template.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            template_id: The template ID to use
            filename: Name for the generated document
            data: Template variable data to fill in

        Returns:
            Created document object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            template_id: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
            filename: "contract.pdf"
            data:
              name: "John Doe"
              value: "10000"
        """
        body = {
            "data": {
                "type": "documents",
                "attributes": {
                    "filename": filename,
                    "template": {
                        "id": template_id,
                        "data": data,
                    },
                },
            }
        }
        return await client.post(f"/envelopes/{envelope_id}/documents", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_add_document_from_upload(
        client: ClicksignClient,
        envelope_id: str,
        filename: str,
        content_base64: str,
    ) -> Dict[str, Any]:
        """Add a document to an envelope by uploading base64 content.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            filename: Name for the uploaded document
            content_base64: Base64-encoded file content

        Returns:
            Created document object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            filename: "contract.pdf"
            content_base64: "JVBERi0xLjQK..."
        """
        body = {
            "data": {
                "type": "documents",
                "attributes": {
                    "filename": filename,
                    "content_base64": content_base64,
                },
            }
        }
        return await client.post(f"/envelopes/{envelope_id}/documents", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_get_document(
        client: ClicksignClient,
        envelope_id: str,
        document_id: str,
    ) -> Dict[str, Any]:
        """Get a document from an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            document_id: The document ID

        Returns:
            Document object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
        """
        return await client.get(f"/envelopes/{envelope_id}/documents/{document_id}")

    @opcode(category="clicksign")
    async def clicksign_list_documents(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """List all documents in an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            List of documents (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        return await client.get(f"/envelopes/{envelope_id}/documents")

    @opcode(category="clicksign")
    async def clicksign_update_document(
        client: ClicksignClient,
        envelope_id: str,
        document_id: str,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a document in an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            document_id: The document ID
            filename: New filename for the document

        Returns:
            Updated document object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
            filename: "updated_contract.pdf"
        """
        attributes: Dict[str, Any] = {}
        if filename is not None:
            attributes["filename"] = filename

        body = {"data": {"type": "documents", "attributes": attributes}}
        return await client.patch(
            f"/envelopes/{envelope_id}/documents/{document_id}", json_data=body
        )

    @opcode(category="clicksign")
    async def clicksign_delete_document(
        client: ClicksignClient,
        envelope_id: str,
        document_id: str,
    ) -> bool:
        """Delete a document from an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            document_id: The document ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            document_id: "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
        """
        await client.delete(f"/envelopes/{envelope_id}/documents/{document_id}")
        return True

    # ============================================================================
    # Signers
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_add_signer(
        client: ClicksignClient,
        envelope_id: str,
        name: str,
        email: str,
        phone_number: Optional[str] = None,
        documentation: Optional[str] = None,
        has_documentation: bool = False,
        birthday: Optional[str] = None,
        refusable: bool = False,
        group: int = 0,
        communicate_events: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Add a signer to an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            name: Full name of the signer (must have at least 2 words)
            email: Email address of the signer
            phone_number: Phone number with country code (e.g., "+5511999999999")
            documentation: CPF or CNPJ document number
            has_documentation: Whether the signer has documentation (default: False)
            birthday: Birthday in ISO 8601 format (e.g., "1990-01-15")
            refusable: Whether the signer can refuse to sign (default: False)
            group: Signing group/order (default: 0)
            communicate_events: Event notification config (e.g., {"sign": "email"})

        Returns:
            Created signer object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            name: "John Doe"
            email: "john@example.com"
            phone_number: "+5511999999999"
            refusable: true
        """
        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")
        if len(name.strip().split()) < 2:
            raise ValueError("name must have at least 2 words (first and last name)")

        attributes: Dict[str, Any] = {
            "name": name,
            "email": email,
            "has_documentation": has_documentation,
            "refusable": refusable,
            "group": group,
        }
        if phone_number is not None:
            attributes["phone_number"] = phone_number
        if documentation is not None:
            attributes["documentation"] = documentation
        if birthday is not None:
            attributes["birthday"] = birthday
        if communicate_events is not None:
            attributes["communicate_events"] = communicate_events

        body = {"data": {"type": "signers", "attributes": attributes}}
        return await client.post(f"/envelopes/{envelope_id}/signers", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_get_signer(
        client: ClicksignClient,
        envelope_id: str,
        signer_id: str,
    ) -> Dict[str, Any]:
        """Get a signer from an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            signer_id: The signer ID

        Returns:
            Signer object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
        """
        return await client.get(f"/envelopes/{envelope_id}/signers/{signer_id}")

    @opcode(category="clicksign")
    async def clicksign_list_signers(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """List all signers in an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            List of signers (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        return await client.get(f"/envelopes/{envelope_id}/signers")

    @opcode(category="clicksign")
    async def clicksign_delete_signer(
        client: ClicksignClient,
        envelope_id: str,
        signer_id: str,
    ) -> bool:
        """Delete a signer from an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            signer_id: The signer ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
        """
        await client.delete(f"/envelopes/{envelope_id}/signers/{signer_id}")
        return True

    # ============================================================================
    # Requirements (Qualifications & Authentications)
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_add_qualification(
        client: ClicksignClient,
        envelope_id: str,
        document_id: str,
        signer_id: str,
        action: str = "agree",
        role: str = "sign",
    ) -> Dict[str, Any]:
        """Add a signing qualification requirement to an envelope.

        Links a signer to a document with a specific action and role.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            document_id: The document ID
            signer_id: The signer ID
            action: Action type (e.g., "agree", "sign", "approve", "acknowledge")
            role: Signer role (e.g., "sign", "witness", "intervening", "receipt")

        Returns:
            Created requirement object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            document_id: "dddddddd-dddd-dddd-dddd-dddddddddddd"
            signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
            action: "agree"
            role: "sign"
        """
        body = {
            "data": {
                "type": "requirements",
                "attributes": {
                    "action": action,
                    "role": role,
                },
                "relationships": {
                    "document": {"data": {"type": "documents", "id": document_id}},
                    "signer": {"data": {"type": "signers", "id": signer_id}},
                },
            }
        }
        return await client.post(
            f"/envelopes/{envelope_id}/requirements", json_data=body
        )

    @opcode(category="clicksign")
    async def clicksign_add_authentication(
        client: ClicksignClient,
        envelope_id: str,
        document_id: str,
        signer_id: str,
        auth: str = "email",
    ) -> Dict[str, Any]:
        """Add an authentication requirement to an envelope.

        Requires a signer to provide evidence (e.g., email, SMS, selfie)
        before signing a document.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            document_id: The document ID
            signer_id: The signer ID
            auth: Authentication type (e.g., "email", "sms", "pix", "selfie",
                "handwritten", "liveness", "official_document", "icpbr_certificate")

        Returns:
            Created requirement object (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            document_id: "dddddddd-dddd-dddd-dddd-dddddddddddd"
            signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
            auth: "email"
        """
        body = {
            "data": {
                "type": "requirements",
                "attributes": {
                    "action": "provide_evidence",
                    "auth": auth,
                },
                "relationships": {
                    "document": {"data": {"type": "documents", "id": document_id}},
                    "signer": {"data": {"type": "signers", "id": signer_id}},
                },
            }
        }
        return await client.post(
            f"/envelopes/{envelope_id}/requirements", json_data=body
        )

    @opcode(category="clicksign")
    async def clicksign_list_requirements(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """List all requirements in an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            List of requirements (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        return await client.get(f"/envelopes/{envelope_id}/requirements")

    @opcode(category="clicksign")
    async def clicksign_delete_requirement(
        client: ClicksignClient,
        envelope_id: str,
        requirement_id: str,
    ) -> bool:
        """Delete a requirement from an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            requirement_id: The requirement ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            requirement_id: "rrrrrrrr-rrrr-rrrr-rrrr-rrrrrrrrrrrr"
        """
        await client.delete(f"/envelopes/{envelope_id}/requirements/{requirement_id}")
        return True

    @opcode(category="clicksign")
    async def clicksign_batch_requirements(
        client: ClicksignClient,
        envelope_id: str,
        requirements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create multiple requirements in a single batch request.

        Each requirement in the list should contain action, role (or auth),
        document_id, and signer_id.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            requirements: List of requirement dicts, each with keys:
                - action: Action type (e.g., "agree", "provide_evidence")
                - document_id: The document ID
                - signer_id: The signer ID
                - role: Signer role (for qualifications)
                - auth: Auth type (for authentications)

        Returns:
            Batch creation response (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            requirements:
              - action: "agree"
                role: "sign"
                document_id: "doc-id-1"
                signer_id: "signer-id-1"
              - action: "provide_evidence"
                auth: "email"
                document_id: "doc-id-1"
                signer_id: "signer-id-1"
        """
        items = []
        for req in requirements:
            attributes: Dict[str, Any] = {"action": req["action"]}
            if "role" in req:
                attributes["role"] = req["role"]
            if "auth" in req:
                attributes["auth"] = req["auth"]

            item = {
                "type": "requirements",
                "attributes": attributes,
                "relationships": {
                    "document": {
                        "data": {"type": "documents", "id": req["document_id"]}
                    },
                    "signer": {"data": {"type": "signers", "id": req["signer_id"]}},
                },
            }
            items.append(item)

        body = {"data": items}
        return await client.post(
            f"/envelopes/{envelope_id}/requirements/batch", json_data=body
        )

    # ============================================================================
    # Notifications
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_notify_signer(
        client: ClicksignClient,
        envelope_id: str,
        signer_id: str,
    ) -> Dict[str, Any]:
        """Send a notification to a specific signer.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID
            signer_id: The signer ID to notify

        Returns:
            Notification response (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            signer_id: "ssssssss-ssss-ssss-ssss-ssssssssssss"
        """
        body = {"data": {"type": "notifications", "attributes": {}}}
        return await client.post(
            f"/envelopes/{envelope_id}/signers/{signer_id}/notifications",
            json_data=body,
        )

    @opcode(category="clicksign")
    async def clicksign_notify_all(
        client: ClicksignClient,
        envelope_id: str,
    ) -> Dict[str, Any]:
        """Send notifications to all pending signers in an envelope.

        Args:
            client: ClicksignClient from clicksign_create_client
            envelope_id: The envelope ID

        Returns:
            Notification response (JSON:API response)

        Example:
            client: { node: create_client }
            envelope_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        body = {"data": {"type": "notifications", "attributes": {}}}
        return await client.post(
            f"/envelopes/{envelope_id}/notifications", json_data=body
        )

    # ============================================================================
    # Templates
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_list_templates(
        client: ClicksignClient,
    ) -> Dict[str, Any]:
        """List all available document templates.

        Args:
            client: ClicksignClient from clicksign_create_client

        Returns:
            List of templates (JSON:API response)

        Example:
            client: { node: create_client }
        """
        return await client.get("/templates")

    @opcode(category="clicksign")
    async def clicksign_get_template(
        client: ClicksignClient,
        template_id: str,
    ) -> Dict[str, Any]:
        """Get a template by ID.

        Args:
            client: ClicksignClient from clicksign_create_client
            template_id: The template ID

        Returns:
            Template object (JSON:API response)

        Example:
            client: { node: create_client }
            template_id: "tttttttt-tttt-tttt-tttt-tttttttttttt"
        """
        return await client.get(f"/templates/{template_id}")

    # ============================================================================
    # Webhooks
    # ============================================================================

    @opcode(category="clicksign")
    async def clicksign_create_webhook(
        client: ClicksignClient,
        url: str,
        events: List[str],
    ) -> Dict[str, Any]:
        """Create a webhook subscription for envelope events.

        Args:
            client: ClicksignClient from clicksign_create_client
            url: URL to receive webhook POST requests
            events: List of event types to subscribe to (e.g.,
                ["envelope.closed", "signer.signed", "envelope.canceled"])

        Returns:
            Created webhook object (JSON:API response)

        Example:
            client: { node: create_client }
            url: "https://my-app.com/webhooks/clicksign"
            events:
              - "envelope.closed"
              - "signer.signed"
        """
        body = {
            "data": {
                "type": "webhooks",
                "attributes": {
                    "url": url,
                    "events": events,
                },
            }
        }
        return await client.post("/webhooks", json_data=body)

    @opcode(category="clicksign")
    async def clicksign_list_webhooks(
        client: ClicksignClient,
    ) -> Dict[str, Any]:
        """List all webhook subscriptions.

        Args:
            client: ClicksignClient from clicksign_create_client

        Returns:
            List of webhooks (JSON:API response)

        Example:
            client: { node: create_client }
        """
        return await client.get("/webhooks")

    @opcode(category="clicksign")
    async def clicksign_delete_webhook(
        client: ClicksignClient,
        webhook_id: str,
    ) -> bool:
        """Delete a webhook subscription.

        Args:
            client: ClicksignClient from clicksign_create_client
            webhook_id: The webhook ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            webhook_id: "wwwwwwww-wwww-wwww-wwww-wwwwwwwwwwww"
        """
        await client.delete(f"/webhooks/{webhook_id}")
        return True
