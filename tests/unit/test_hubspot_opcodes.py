"""Tests for HubSpot CRM opcodes."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from lexflow import default_registry
from lexflow.opcodes.opcodes_hubspot import (
    _validate_object_type,
    _validate_id,
    _get_association_type_id,
    ASSOCIATION_TYPE_IDS,
    VALID_OBJECT_TYPES,
    HubSpotClient,
)

pytestmark = pytest.mark.asyncio


# ============================================================================
# Validation helpers
# ============================================================================


class TestValidateObjectType:
    def test_valid_types(self):
        for obj_type in VALID_OBJECT_TYPES:
            assert _validate_object_type(obj_type) == obj_type

    def test_normalizes_case_and_whitespace(self):
        assert _validate_object_type("  Contacts  ") == "contacts"
        assert _validate_object_type("DEALS") == "deals"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid object type"):
            _validate_object_type("invalid_type")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid object type"):
            _validate_object_type("")


class TestValidateId:
    def test_valid_alphanumeric(self):
        _validate_id("12345", "test_id")
        _validate_id("abc123", "test_id")

    def test_numeric_value_coerced_to_str(self):
        _validate_id(12345, "test_id")

    def test_invalid_id_with_special_chars(self):
        with pytest.raises(ValueError, match="Must be alphanumeric"):
            _validate_id("12/345", "test_id")

    def test_path_traversal_attempt(self):
        with pytest.raises(ValueError, match="Must be alphanumeric"):
            _validate_id("../etc/passwd", "test_id")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Must be alphanumeric"):
            _validate_id("", "test_id")


class TestGetAssociationTypeId:
    def test_explicit_override(self):
        assert _get_association_type_id("contacts", "companies", 999) == 999

    def test_known_pairs(self):
        assert _get_association_type_id("contacts", "companies") == 1
        assert _get_association_type_id("companies", "contacts") == 2
        assert _get_association_type_id("deals", "contacts") == 3
        assert _get_association_type_id("tickets", "deals") == 28
        assert _get_association_type_id("deals", "tickets") == 28

    def test_unknown_pair_raises(self):
        with pytest.raises(ValueError, match="Unknown association type"):
            _get_association_type_id("products", "quotes")

    def test_no_duplicate_values_per_key(self):
        """Verify all association type ID keys are unique (no dict key collision)."""
        keys = list(ASSOCIATION_TYPE_IDS.keys())
        assert len(keys) == len(set(keys))


# ============================================================================
# HubSpotClient
# ============================================================================


def _mock_client():
    """Create a HubSpotClient with a mocked aiohttp session."""
    with patch("lexflow.opcodes.opcodes_hubspot.aiohttp.ClientSession"):
        client = HubSpotClient("test-token")

    # Replace session with a mock
    client._session = MagicMock()
    return client


def _mock_response(status=200, json_data=None):
    """Create a mock aiohttp response as an async context manager."""
    response = AsyncMock()
    response.status = status
    response.json = AsyncMock(return_value=json_data or {})

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


class TestHubSpotClientRequest:
    async def test_successful_get(self):
        client = _mock_client()
        expected = {"id": "123", "properties": {"email": "test@test.com"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await client.get("/crm/v3/objects/contacts/123")
        assert result == expected
        client._session.request.assert_called_once_with(
            "GET",
            f"{client.base_url}/crm/v3/objects/contacts/123",
            params=None,
            json=None,
        )

    async def test_status_204_returns_empty_dict(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await client.delete("/crm/v3/objects/contacts/123")
        assert result == {}

    async def test_error_response_raises_valueerror(self):
        client = _mock_client()
        error_data = {
            "message": "Contact not found",
            "category": "OBJECT_NOT_FOUND",
            "correlationId": "abc-123",
        }
        client._session.request = MagicMock(
            return_value=_mock_response(404, error_data)
        )

        with pytest.raises(ValueError, match="HubSpot API error \\(404\\)"):
            await client.get("/crm/v3/objects/contacts/999")

    async def test_error_response_includes_category_and_correlation(self):
        client = _mock_client()
        error_data = {
            "message": "Bad request",
            "category": "VALIDATION_ERROR",
            "correlationId": "xyz-789",
        }
        client._session.request = MagicMock(
            return_value=_mock_response(400, error_data)
        )

        with pytest.raises(ValueError, match="Category: VALIDATION_ERROR"):
            await client.post("/crm/v3/objects/contacts", json_data={})

    async def test_error_response_minimal_fields(self):
        client = _mock_client()
        error_data = {"message": "Server error"}
        client._session.request = MagicMock(
            return_value=_mock_response(500, error_data)
        )

        with pytest.raises(ValueError, match="Server error"):
            await client.get("/test")

    async def test_post_sends_json_data(self):
        client = _mock_client()
        body = {"properties": {"email": "test@test.com"}}
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "1"})
        )

        await client.post("/crm/v3/objects/contacts", json_data=body)
        client._session.request.assert_called_once_with(
            "POST",
            f"{client.base_url}/crm/v3/objects/contacts",
            params=None,
            json=body,
        )

    async def test_patch_method(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "1"})
        )

        await client.patch("/endpoint", json_data={"key": "val"})
        client._session.request.assert_called_once_with(
            "PATCH",
            f"{client.base_url}/endpoint",
            params=None,
            json={"key": "val"},
        )

    async def test_put_method(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"ok": True})
        )

        await client.put("/endpoint", json_data={"data": 1})
        client._session.request.assert_called_once_with(
            "PUT",
            f"{client.base_url}/endpoint",
            params=None,
            json={"data": 1},
        )


# ============================================================================
# Opcodes via registry
# ============================================================================


class TestHubSpotCreateClient:
    async def test_creates_client(self):
        with patch("lexflow.opcodes.opcodes_hubspot.aiohttp.ClientSession"):
            client = await default_registry.call(
                "hubspot_create_client", ["test-token"]
            )
        assert isinstance(client, HubSpotClient)
        assert client.access_token == "test-token"

    async def test_empty_token_raises(self):
        with pytest.raises(ValueError, match="access_token is required"):
            await default_registry.call("hubspot_create_client", [""])


class TestHubSpotCloseClient:
    async def test_closes_session(self):
        client = _mock_client()
        client._session.close = AsyncMock()

        result = await default_registry.call("hubspot_close_client", [client])
        assert result is True
        client._session.close.assert_awaited_once()


class TestHubSpotContactOpcodes:
    async def test_get_contact(self):
        client = _mock_client()
        expected = {"id": "123", "properties": {"email": "a@b.com"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("hubspot_get_contact", [client, "123"])
        assert result == expected

    async def test_get_contact_with_properties(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "1"})
        )

        await default_registry.call(
            "hubspot_get_contact", [client, "123", ["email", "firstname"]]
        )
        call_args = client._session.request.call_args
        assert call_args[1]["params"] == {"properties": "email,firstname"}

    async def test_get_contact_invalid_id(self):
        client = _mock_client()
        with pytest.raises(ValueError, match="Must be alphanumeric"):
            await default_registry.call("hubspot_get_contact", [client, "../hack"])

    async def test_search_contacts(self):
        client = _mock_client()
        search_result = {"results": [{"id": "1"}], "total": 1}
        client._session.request = MagicMock(
            return_value=_mock_response(200, search_result)
        )

        filters = [{"propertyName": "email", "operator": "EQ", "value": "a@b.com"}]
        result = await default_registry.call(
            "hubspot_search_contacts", [client, filters]
        )
        assert result == search_result

    async def test_search_contacts_limit_capped(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"results": [], "total": 0})
        )

        await default_registry.call("hubspot_search_contacts", [client, [], None, 500])
        call_args = client._session.request.call_args
        body = call_args[1]["json"]
        assert body["limit"] == 100

    async def test_create_contact(self):
        client = _mock_client()
        created = {"id": "999", "properties": {"email": "new@b.com"}}
        client._session.request = MagicMock(return_value=_mock_response(200, created))

        result = await default_registry.call(
            "hubspot_create_contact", [client, {"email": "new@b.com"}]
        )
        assert result["id"] == "999"

    async def test_update_contact(self):
        client = _mock_client()
        updated = {"id": "123", "properties": {"firstname": "Jane"}}
        client._session.request = MagicMock(return_value=_mock_response(200, updated))

        result = await default_registry.call(
            "hubspot_update_contact", [client, "123", {"firstname": "Jane"}]
        )
        assert result["properties"]["firstname"] == "Jane"

    async def test_delete_contact(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call("hubspot_delete_contact", [client, "123"])
        assert result is True


class TestHubSpotCompanyOpcodes:
    async def test_get_company(self):
        client = _mock_client()
        expected = {"id": "456", "properties": {"name": "Acme"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("hubspot_get_company", [client, "456"])
        assert result == expected

    async def test_search_companies(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"results": [], "total": 0})
        )

        filters = [{"propertyName": "domain", "operator": "EQ", "value": "acme.com"}]
        result = await default_registry.call(
            "hubspot_search_companies", [client, filters]
        )
        assert "results" in result

    async def test_create_company(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "789"})
        )

        result = await default_registry.call(
            "hubspot_create_company", [client, {"name": "Acme"}]
        )
        assert result["id"] == "789"

    async def test_update_company(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "456"})
        )

        result = await default_registry.call(
            "hubspot_update_company", [client, "456", {"industry": "Tech"}]
        )
        assert result["id"] == "456"


class TestHubSpotDealOpcodes:
    async def test_get_deal(self):
        client = _mock_client()
        expected = {"id": "111", "properties": {"dealname": "Big Deal"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("hubspot_get_deal", [client, "111"])
        assert result == expected

    async def test_search_deals(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"results": [], "total": 0})
        )

        filters = [
            {"propertyName": "dealstage", "operator": "EQ", "value": "closedwon"}
        ]
        result = await default_registry.call("hubspot_search_deals", [client, filters])
        assert "results" in result

    async def test_create_deal(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "222"})
        )

        result = await default_registry.call(
            "hubspot_create_deal", [client, {"dealname": "New Deal"}]
        )
        assert result["id"] == "222"

    async def test_update_deal(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"id": "111"})
        )

        result = await default_registry.call(
            "hubspot_update_deal", [client, "111", {"amount": "5000"}]
        )
        assert result["id"] == "111"


class TestHubSpotAssociateOpcode:
    async def test_associate_with_auto_inferred_type(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"status": "ok"})
        )

        result = await default_registry.call(
            "hubspot_associate",
            [client, "contacts", "123", "companies", "456"],
        )
        assert result == {"status": "ok"}

        call_args = client._session.request.call_args
        assert call_args[1]["json"] == [
            {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}
        ]

    async def test_associate_with_explicit_type(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"status": "ok"})
        )

        await default_registry.call(
            "hubspot_associate",
            [client, "contacts", "123", "companies", "456", 999],
        )

        call_args = client._session.request.call_args
        assert call_args[1]["json"] == [
            {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 999}
        ]

    async def test_associate_invalid_from_type(self):
        client = _mock_client()
        with pytest.raises(ValueError, match="Invalid object type"):
            await default_registry.call(
                "hubspot_associate",
                [client, "invalid", "123", "companies", "456"],
            )

    async def test_associate_invalid_id(self):
        client = _mock_client()
        with pytest.raises(ValueError, match="Must be alphanumeric"):
            await default_registry.call(
                "hubspot_associate",
                [client, "contacts", "../hack", "companies", "456"],
            )

    async def test_associate_unknown_pair_raises(self):
        client = _mock_client()
        with pytest.raises(ValueError, match="Unknown association type"):
            await default_registry.call(
                "hubspot_associate",
                [client, "products", "1", "quotes", "2"],
            )

    async def test_associate_uses_v4_endpoint(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(200, {}))

        await default_registry.call(
            "hubspot_associate",
            [client, "contacts", "123", "companies", "456"],
        )

        call_args = client._session.request.call_args
        url = call_args[0][1]
        assert "/crm/v4/objects/" in url


class TestHubSpotUtilityOpcodes:
    async def test_list_properties(self):
        client = _mock_client()
        props = [{"name": "email", "label": "Email", "type": "string"}]
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"results": props})
        )

        result = await default_registry.call(
            "hubspot_list_properties", [client, "contacts"]
        )
        assert result == props

    async def test_list_properties_invalid_type(self):
        client = _mock_client()
        with pytest.raises(ValueError, match="Invalid object type"):
            await default_registry.call("hubspot_list_properties", [client, "invalid"])

    async def test_test_connection_success(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(200, {"results": []})
        )

        result = await default_registry.call("hubspot_test_connection", [client])
        assert result is True

    async def test_test_connection_failure(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(401, {"message": "Unauthorized"})
        )

        with pytest.raises(ValueError, match="HubSpot API error \\(401\\)"):
            await default_registry.call("hubspot_test_connection", [client])


class TestOpcodeRegistration:
    def test_all_hubspot_opcodes_registered(self):
        opcodes = default_registry.list_opcodes()
        expected = [
            "hubspot_create_client",
            "hubspot_close_client",
            "hubspot_get_contact",
            "hubspot_search_contacts",
            "hubspot_create_contact",
            "hubspot_update_contact",
            "hubspot_delete_contact",
            "hubspot_get_company",
            "hubspot_search_companies",
            "hubspot_create_company",
            "hubspot_update_company",
            "hubspot_get_deal",
            "hubspot_search_deals",
            "hubspot_create_deal",
            "hubspot_update_deal",
            "hubspot_associate",
            "hubspot_list_properties",
            "hubspot_test_connection",
        ]
        for name in expected:
            assert name in opcodes, f"Opcode '{name}' not registered"
