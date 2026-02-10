"""HubSpot CRM opcodes for LexFlow.

This module provides opcodes for interacting with HubSpot CRM API,
enabling CRM automation workflows similar to n8n/Zapier.

Installation:
    pip install lexflow[hubspot]
    or:
    pip install aiohttp

Authentication:
    HubSpot uses OAuth2 access tokens. Generate a private app token at:
    https://developers.hubspot.com/docs/api/private-apps
"""

from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import aiohttp

    HUBSPOT_AVAILABLE = True
except ImportError:
    HUBSPOT_AVAILABLE = False


def _check_hubspot():
    """Check if HubSpot dependencies are available."""
    if not HUBSPOT_AVAILABLE:
        raise ImportError(
            "HubSpot dependencies not installed. Install with:\n"
            "  pip install lexflow[hubspot]\n"
            "or:\n"
            "  pip install aiohttp"
        )


class HubSpotClient:
    """Reusable HubSpot API client."""

    def __init__(self, access_token: str, base_url: str = "https://api.hubapi.com"):
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to HubSpot API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, params=params, json=json_data, headers=headers
            ) as response:
                if response.status == 204:
                    return {}

                data = await response.json()

                if response.status >= 400:
                    error_msg = data.get("message", str(data))
                    raise ValueError(
                        f"HubSpot API error ({response.status}): {error_msg}"
                    )

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

    async def put(
        self, endpoint: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._request("PUT", endpoint, json_data=json_data)


def register_hubspot_opcodes():
    """Register HubSpot opcodes to the default registry."""
    if not HUBSPOT_AVAILABLE:
        return

    register_category(
        id="hubspot",
        label="HubSpot Operations",
        prefix="hubspot_",
        color="#FF7A59",
        icon="hubspot",
        requires="hubspot",
        order=215,
    )

    # ============================================================================
    # Authentication
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_create_client(
        access_token: str,
        base_url: str = "https://api.hubapi.com",
    ) -> HubSpotClient:
        """Create a HubSpot API client for CRM operations.

        Args:
            access_token: HubSpot private app access token
            base_url: HubSpot API base URL (default: https://api.hubapi.com)

        Returns:
            HubSpotClient object to use with other hubspot_* opcodes

        Example:
            access_token: "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        _check_hubspot()
        return HubSpotClient(access_token, base_url)

    # ============================================================================
    # Contacts
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_get_contact(
        client: HubSpotClient,
        contact_id: str,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a contact by ID from HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            contact_id: The HubSpot contact ID
            properties: List of property names to return (default: all)

        Returns:
            Contact object with id, properties, createdAt, updatedAt

        Example:
            client: { node: create_client }
            contact_id: "12345"
            properties: ["firstname", "lastname", "email"]
        """
        _check_hubspot()

        params = {}
        if properties:
            params["properties"] = ",".join(properties)

        return await client.get(f"/crm/v3/objects/contacts/{contact_id}", params=params)

    @opcode(category="hubspot")
    async def hubspot_search_contacts(
        client: HubSpotClient,
        filters: List[Dict[str, Any]],
        properties: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Search contacts in HubSpot using filters.

        Args:
            client: HubSpotClient from hubspot_create_client
            filters: List of filter objects with propertyName, operator, value.
                Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
            properties: List of property names to return
            limit: Maximum number of results (default: 100, max: 100)

        Returns:
            Dict with 'results' list and 'total' count

        Example:
            client: { node: create_client }
            filters:
              - propertyName: "email"
                operator: "EQ"
                value: "test@example.com"
            properties: ["firstname", "lastname", "email"]
            limit: 10
        """
        _check_hubspot()

        body: Dict[str, Any] = {
            "filterGroups": [{"filters": filters}],
            "limit": min(limit, 100),
        }
        if properties:
            body["properties"] = properties

        return await client.post("/crm/v3/objects/contacts/search", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_create_contact(
        client: HubSpotClient,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new contact in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            properties: Dict of contact properties (e.g., firstname, lastname, email)

        Returns:
            Created contact object with id, properties, createdAt

        Example:
            client: { node: create_client }
            properties:
              firstname: "John"
              lastname: "Doe"
              email: "john.doe@example.com"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.post("/crm/v3/objects/contacts", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_update_contact(
        client: HubSpotClient,
        contact_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing contact in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            contact_id: The HubSpot contact ID
            properties: Dict of contact properties to update

        Returns:
            Updated contact object

        Example:
            client: { node: create_client }
            contact_id: "12345"
            properties:
              firstname: "Jane"
              phone: "+1234567890"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.patch(
            f"/crm/v3/objects/contacts/{contact_id}", json_data=body
        )

    @opcode(category="hubspot")
    async def hubspot_delete_contact(
        client: HubSpotClient,
        contact_id: str,
    ) -> bool:
        """Delete a contact from HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            contact_id: The HubSpot contact ID

        Returns:
            True if deletion was successful

        Example:
            client: { node: create_client }
            contact_id: "12345"
        """
        _check_hubspot()

        await client.delete(f"/crm/v3/objects/contacts/{contact_id}")
        return True

    # ============================================================================
    # Companies
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_get_company(
        client: HubSpotClient,
        company_id: str,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a company by ID from HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            company_id: The HubSpot company ID
            properties: List of property names to return (default: all)

        Returns:
            Company object with id, properties, createdAt, updatedAt

        Example:
            client: { node: create_client }
            company_id: "67890"
            properties: ["name", "domain", "industry"]
        """
        _check_hubspot()

        params = {}
        if properties:
            params["properties"] = ",".join(properties)

        return await client.get(
            f"/crm/v3/objects/companies/{company_id}", params=params
        )

    @opcode(category="hubspot")
    async def hubspot_search_companies(
        client: HubSpotClient,
        filters: List[Dict[str, Any]],
        properties: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Search companies in HubSpot using filters.

        Args:
            client: HubSpotClient from hubspot_create_client
            filters: List of filter objects with propertyName, operator, value.
                Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
            properties: List of property names to return
            limit: Maximum number of results (default: 100, max: 100)

        Returns:
            Dict with 'results' list and 'total' count

        Example:
            client: { node: create_client }
            filters:
              - propertyName: "domain"
                operator: "EQ"
                value: "hubspot.com"
            properties: ["name", "domain", "industry"]
            limit: 10
        """
        _check_hubspot()

        body: Dict[str, Any] = {
            "filterGroups": [{"filters": filters}],
            "limit": min(limit, 100),
        }
        if properties:
            body["properties"] = properties

        return await client.post("/crm/v3/objects/companies/search", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_create_company(
        client: HubSpotClient,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new company in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            properties: Dict of company properties (e.g., name, domain, industry)

        Returns:
            Created company object with id, properties, createdAt

        Example:
            client: { node: create_client }
            properties:
              name: "Acme Corp"
              domain: "acme.com"
              industry: "Technology"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.post("/crm/v3/objects/companies", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_update_company(
        client: HubSpotClient,
        company_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing company in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            company_id: The HubSpot company ID
            properties: Dict of company properties to update

        Returns:
            Updated company object

        Example:
            client: { node: create_client }
            company_id: "67890"
            properties:
              industry: "Software"
              numberofemployees: "100"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.patch(
            f"/crm/v3/objects/companies/{company_id}", json_data=body
        )

    # ============================================================================
    # Deals
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_get_deal(
        client: HubSpotClient,
        deal_id: str,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a deal by ID from HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            deal_id: The HubSpot deal ID
            properties: List of property names to return (default: all)

        Returns:
            Deal object with id, properties, createdAt, updatedAt

        Example:
            client: { node: create_client }
            deal_id: "11111"
            properties: ["dealname", "amount", "dealstage"]
        """
        _check_hubspot()

        params = {}
        if properties:
            params["properties"] = ",".join(properties)

        return await client.get(f"/crm/v3/objects/deals/{deal_id}", params=params)

    @opcode(category="hubspot")
    async def hubspot_search_deals(
        client: HubSpotClient,
        filters: List[Dict[str, Any]],
        properties: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Search deals in HubSpot using filters.

        Args:
            client: HubSpotClient from hubspot_create_client
            filters: List of filter objects with propertyName, operator, value.
                Operators: EQ, NEQ, LT, LTE, GT, GTE, IN, NOT_IN, CONTAINS
            properties: List of property names to return
            limit: Maximum number of results (default: 100, max: 100)

        Returns:
            Dict with 'results' list and 'total' count

        Example:
            client: { node: create_client }
            filters:
              - propertyName: "dealstage"
                operator: "EQ"
                value: "closedwon"
            properties: ["dealname", "amount", "dealstage"]
            limit: 10
        """
        _check_hubspot()

        body: Dict[str, Any] = {
            "filterGroups": [{"filters": filters}],
            "limit": min(limit, 100),
        }
        if properties:
            body["properties"] = properties

        return await client.post("/crm/v3/objects/deals/search", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_create_deal(
        client: HubSpotClient,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new deal in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            properties: Dict of deal properties (e.g., dealname, amount, dealstage)

        Returns:
            Created deal object with id, properties, createdAt

        Example:
            client: { node: create_client }
            properties:
              dealname: "New Business Deal"
              amount: "10000"
              dealstage: "appointmentscheduled"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.post("/crm/v3/objects/deals", json_data=body)

    @opcode(category="hubspot")
    async def hubspot_update_deal(
        client: HubSpotClient,
        deal_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing deal in HubSpot.

        Args:
            client: HubSpotClient from hubspot_create_client
            deal_id: The HubSpot deal ID
            properties: Dict of deal properties to update

        Returns:
            Updated deal object

        Example:
            client: { node: create_client }
            deal_id: "11111"
            properties:
              amount: "15000"
              dealstage: "closedwon"
        """
        _check_hubspot()

        body = {"properties": properties}
        return await client.patch(f"/crm/v3/objects/deals/{deal_id}", json_data=body)

    # ============================================================================
    # Associations
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_associate(
        client: HubSpotClient,
        from_type: str,
        from_id: str,
        to_type: str,
        to_id: str,
        association_type: str,
    ) -> Dict[str, Any]:
        """Create an association between two HubSpot objects.

        Args:
            client: HubSpotClient from hubspot_create_client
            from_type: Source object type (contacts, companies, deals)
            from_id: Source object ID
            to_type: Target object type (contacts, companies, deals)
            to_id: Target object ID
            association_type: Association type ID or label (e.g., "contact_to_company")

        Returns:
            Association response object

        Example - Associate contact with company:
            client: { node: create_client }
            from_type: "contacts"
            from_id: "12345"
            to_type: "companies"
            to_id: "67890"
            association_type: "contact_to_company"

        Example - Associate deal with contact:
            client: { node: create_client }
            from_type: "deals"
            from_id: "11111"
            to_type: "contacts"
            to_id: "12345"
            association_type: "deal_to_contact"
        """
        _check_hubspot()

        endpoint = (
            f"/crm/v4/objects/{from_type}/{from_id}/associations/{to_type}/{to_id}"
        )

        body = [
            {
                "associationCategory": "HUBSPOT_DEFINED",
                "associationTypeId": association_type,
            }
        ]

        # Try numeric association type first
        try:
            type_id = int(association_type)
            body = [
                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": type_id}
            ]
        except ValueError:
            # Use label-based association
            body = [
                {
                    "associationCategory": "USER_DEFINED",
                    "associationTypeId": association_type,
                }
            ]

        return await client.put(endpoint, json_data=body)

    # ============================================================================
    # Utilities
    # ============================================================================

    @opcode(category="hubspot")
    async def hubspot_list_properties(
        client: HubSpotClient,
        object_type: str,
    ) -> List[Dict[str, Any]]:
        """List all properties for a HubSpot object type.

        Args:
            client: HubSpotClient from hubspot_create_client
            object_type: Object type (contacts, companies, deals)

        Returns:
            List of property objects with name, label, type, description

        Example:
            client: { node: create_client }
            object_type: "contacts"
        """
        _check_hubspot()

        response = await client.get(f"/crm/v3/properties/{object_type}")
        return response.get("results", [])

    @opcode(category="hubspot")
    async def hubspot_test_connection(
        client: HubSpotClient,
    ) -> bool:
        """Test connection to HubSpot API.

        Args:
            client: HubSpotClient from hubspot_create_client

        Returns:
            True if connection successful, raises exception otherwise

        Example:
            client: { node: create_client }
        """
        _check_hubspot()

        # Test by fetching contact properties (lightweight call)
        await client.get("/crm/v3/properties/contacts")
        return True
