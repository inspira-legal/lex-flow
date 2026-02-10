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


# Valid HubSpot object types (for path validation)
VALID_OBJECT_TYPES = {
    "contacts",
    "companies",
    "deals",
    "tickets",
    "line_items",
    "products",
    "quotes",
}

# Default association type IDs (HubSpot v4 API)
# See: https://developers.hubspot.com/docs/api/crm/associations
ASSOCIATION_TYPE_IDS = {
    # contact ↔ company
    ("contacts", "companies"): 1,
    ("companies", "contacts"): 2,
    # deal ↔ contact
    ("deals", "contacts"): 3,
    ("contacts", "deals"): 4,
    # deal ↔ company
    ("deals", "companies"): 5,
    ("companies", "deals"): 6,
    # ticket ↔ contact
    ("tickets", "contacts"): 15,
    ("contacts", "tickets"): 16,
    # ticket ↔ company
    ("tickets", "companies"): 26,
    ("companies", "tickets"): 27,
    # ticket ↔ deal
    ("tickets", "deals"): 27,
    ("deals", "tickets"): 28,
}


def _validate_object_type(object_type: str) -> str:
    """Validate and normalize HubSpot object type."""
    normalized = object_type.lower().strip()
    if normalized not in VALID_OBJECT_TYPES:
        raise ValueError(
            f"Invalid object type: '{object_type}'. "
            f"Valid types: {', '.join(sorted(VALID_OBJECT_TYPES))}"
        )
    return normalized


def _validate_id(value: str, name: str = "id") -> str:
    """Validate that an ID is safe for use in URL paths (alphanumeric only)."""
    str_value = str(value)
    if not str_value.isalnum():
        raise ValueError(f"Invalid {name}: '{value}'. Must be alphanumeric.")


def _get_association_type_id(
    from_type: str, to_type: str, association_type: Optional[int] = None
) -> int:
    """Get the numeric association type ID."""
    # If explicit ID provided, use it
    if association_type is not None:
        return int(association_type)

    # Infer from object type pair
    key = (from_type, to_type)
    if key in ASSOCIATION_TYPE_IDS:
        return ASSOCIATION_TYPE_IDS[key]

    raise ValueError(
        f"Unknown association type for {from_type} → {to_type}. "
        f"Please provide a numeric association_type ID. "
        f"See: https://developers.hubspot.com/docs/api/crm/associations"
    )


HUBSPOT_API_BASE_URL = "https://api.hubapi.com"


class HubSpotClient:
    """Reusable HubSpot API client."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = HUBSPOT_API_BASE_URL

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
                    # Only extract safe error fields to avoid leaking PII
                    error_msg = data.get("message", "Unknown error")
                    category = data.get("category", "")
                    correlation_id = data.get("correlationId", "")

                    error_parts = [
                        f"HubSpot API error ({response.status}): {error_msg}"
                    ]
                    if category:
                        error_parts.append(f"Category: {category}")
                    if correlation_id:
                        error_parts.append(f"CorrelationId: {correlation_id}")

                    raise ValueError(". ".join(error_parts))

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
    ) -> HubSpotClient:
        """Create a HubSpot API client for CRM operations.

        Args:
            access_token: HubSpot private app access token

        Returns:
            HubSpotClient object to use with other hubspot_* opcodes

        Example:
            access_token: "pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        """
        _check_hubspot()
        return HubSpotClient(access_token)

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
        _validate_id(contact_id, "contact_id")

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
        _validate_id(contact_id, "contact_id")

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
        _validate_id(contact_id, "contact_id")

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
        _validate_id(company_id, "company_id")

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
        _validate_id(company_id, "company_id")

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
        _validate_id(deal_id, "deal_id")

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
        _validate_id(deal_id, "deal_id")

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
        association_type: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create an association between two HubSpot objects.

        Args:
            client: HubSpotClient from hubspot_create_client
            from_type: Source object type (contacts, companies, deals, tickets)
            from_id: Source object ID
            to_type: Target object type (contacts, companies, deals, tickets)
            to_id: Target object ID
            association_type: Integer association type ID (HubSpot v4 API).
                If not provided, auto-inferred from object types.
                Common IDs: contacts→companies=1, companies→contacts=2,
                deals→contacts=3, contacts→deals=4, deals→companies=5,
                companies→deals=6, tickets→contacts=15, contacts→tickets=16.
                See: https://developers.hubspot.com/docs/api/crm/associations

        Returns:
            Association response object

        Example - Associate contact with company (auto-inferred):
            client: { node: create_client }
            from_type: "contacts"
            from_id: "12345"
            to_type: "companies"
            to_id: "67890"

        Example - Associate with explicit type ID:
            client: { node: create_client }
            from_type: "deals"
            from_id: "11111"
            to_type: "contacts"
            to_id: "12345"
            association_type: 3
        """
        _check_hubspot()

        # Validate object types (prevents path traversal)
        from_type = _validate_object_type(from_type)
        to_type = _validate_object_type(to_type)

        # Validate IDs are alphanumeric (prevents injection)
        _validate_id(from_id, "from_id")
        _validate_id(to_id, "to_id")

        # Get numeric association type ID
        type_id = _get_association_type_id(from_type, to_type, association_type)

        endpoint = (
            f"/crm/v4/objects/{from_type}/{from_id}/associations/{to_type}/{to_id}"
        )

        body = [
            {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": type_id}
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
        object_type = _validate_object_type(object_type)

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
