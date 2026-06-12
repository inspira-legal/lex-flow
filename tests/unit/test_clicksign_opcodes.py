"""Tests for Clicksign digital signing opcodes."""

import importlib.util

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lexflow import default_registry

AIOHTTP_AVAILABLE = importlib.util.find_spec("aiohttp") is not None

try:
    from lexflow_opcodes.clicksign import ClicksignClient
except ImportError:
    pass

pytestmark = pytest.mark.asyncio


# ============================================================================
# Helpers
# ============================================================================


def _mock_client():
    """Create a ClicksignClient with a mocked aiohttp session."""
    with patch("lexflow_opcodes.clicksign.aiohttp.ClientSession"):
        client = ClicksignClient("test-token", sandbox=True)

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


# ============================================================================
# ClicksignClient
# ============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignClient:
    async def test_sandbox_url(self):
        client = _mock_client()
        assert "sandbox" in client.base_url

    async def test_production_url(self):
        with patch("lexflow_opcodes.clicksign.aiohttp.ClientSession"):
            client = ClicksignClient("test-token", sandbox=False)
        assert "app.clicksign.com" in client.base_url

    async def test_repr_hides_token(self):
        client = _mock_client()
        assert "test-token" not in repr(client)

    async def test_error_response_without_errors_array(self):
        client = _mock_client()
        client._session.request = MagicMock(
            return_value=_mock_response(400, {"message": "Bad request"})
        )

        with pytest.raises(ValueError, match="Clicksign API error \\(400\\)"):
            await client.get("/envelopes/invalid")

    async def test_error_response_json_api(self):
        client = _mock_client()
        error_data = {
            "errors": [
                {
                    "detail": "Envelope not found",
                    "code": "not_found",
                }
            ]
        }
        client._session.request = MagicMock(
            return_value=_mock_response(400, error_data)
        )

        with pytest.raises(ValueError, match="Clicksign API error \\(400\\)"):
            await client.get("/envelopes/invalid")


# ============================================================================
# _validate_id
# ============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestValidateId:
    async def test_valid_id(self):
        from lexflow_opcodes.clicksign import _validate_id

        assert _validate_id("abc-123") == "abc-123"

    async def test_strips_whitespace(self):
        from lexflow_opcodes.clicksign import _validate_id

        assert _validate_id("  abc-123  ") == "abc-123"

    async def test_empty_string_raises(self):
        from lexflow_opcodes.clicksign import _validate_id

        with pytest.raises(ValueError, match="id cannot be empty"):
            _validate_id("")

    async def test_whitespace_only_raises(self):
        from lexflow_opcodes.clicksign import _validate_id

        with pytest.raises(ValueError, match="id cannot be empty"):
            _validate_id("   ")


# ============================================================================
# Opcodes via registry
# ============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignCreateClient:
    async def test_creates_client(self):
        with patch("lexflow_opcodes.clicksign.aiohttp.ClientSession"):
            client = await default_registry.call(
                "clicksign_create_client", ["test-token", True]
            )
        assert isinstance(client, ClicksignClient)

    async def test_empty_token_raises_error(self):
        with pytest.raises(ValueError, match="access_token is required"):
            await default_registry.call("clicksign_create_client", [""])


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignCloseClient:
    async def test_closes_session(self):
        client = _mock_client()
        client._session.close = AsyncMock()

        result = await default_registry.call("clicksign_close_client", [client])
        assert result is True
        client._session.close.assert_awaited_once()


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignEnvelopes:
    async def test_create_envelope(self):
        client = _mock_client()
        expected = {"data": {"id": "env-123", "type": "envelopes"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_create_envelope", [client, "Test Envelope"]
        )
        assert result == expected

        client._session.request.assert_called_once()
        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/envelopes" in call_args[0][1]
        body = call_args[1]["json"]
        assert body["data"]["type"] == "envelopes"
        assert body["data"]["attributes"]["name"] == "Test Envelope"
        assert body["data"]["attributes"]["remind_interval"] == 3
        assert isinstance(body["data"]["attributes"]["remind_interval"], int)

    async def test_create_envelope_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            await default_registry.call(
                "clicksign_create_envelope", [_mock_client(), ""]
            )

    async def test_create_envelope_whitespace_name_raises_error(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            await default_registry.call(
                "clicksign_create_envelope", [_mock_client(), "   "]
            )

    async def test_create_envelope_with_deadline(self):
        client = _mock_client()
        expected = {"data": {"id": "env-456", "type": "envelopes"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_create_envelope",
            [
                client,
                "Deadline Envelope",
                "pt-BR",
                True,
                3,
                False,
                "2025-12-31T23:59:59Z",
            ],
        )
        assert result == expected

        call_args = client._session.request.call_args
        body = call_args[1]["json"]
        assert body["data"]["attributes"]["deadline_at"] == "2025-12-31T23:59:59Z"

    async def test_get_envelope(self):
        client = _mock_client()
        expected = {"data": {"id": "env-123", "type": "envelopes"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_get_envelope", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123" in call_args[0][1]

    async def test_list_envelopes_with_filters(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_list_envelopes", [client, "running", "Contract"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        params = call_args[1]["params"]
        assert params["filter[status]"] == "running"
        assert params["filter[name]"] == "Contract"

    async def test_list_envelopes_no_filters(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("clicksign_list_envelopes", [client])
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        params = call_args[1]["params"]
        assert params == {}

    async def test_get_envelope_not_found(self):
        client = _mock_client()
        error_data = {"errors": [{"detail": "Envelope not found", "code": "not_found"}]}
        client._session.request = MagicMock(
            return_value=_mock_response(404, error_data)
        )

        with pytest.raises(ValueError, match="Clicksign API error \\(404\\)"):
            await default_registry.call(
                "clicksign_get_envelope", [client, "invalid-id"]
            )

    async def test_activate_envelope(self):
        client = _mock_client()
        expected = {"data": {"id": "env-123", "attributes": {"status": "running"}}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_activate_envelope", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "PATCH"
        body = call_args[1]["json"]
        assert body["data"]["id"] == "env-123"
        assert body["data"]["attributes"]["status"] == "running"

    async def test_cancel_envelope(self):
        client = _mock_client()
        expected = {"data": {"id": "env-123", "attributes": {"status": "canceled"}}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_cancel_envelope", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "PATCH"
        body = call_args[1]["json"]
        assert body["data"]["attributes"]["status"] == "canceled"

    async def test_delete_envelope(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call(
            "clicksign_delete_envelope", [client, "env-123"]
        )
        assert result is True


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignDocuments:
    async def test_add_document_from_template(self):
        client = _mock_client()
        expected = {"data": {"id": "doc-123", "type": "documents"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_document_from_template",
            [client, "env-123", "tmpl-456", "contract.pdf", {"name": "John"}],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/envelopes/env-123/documents" in call_args[0][1]
        body = call_args[1]["json"]
        assert body["data"]["type"] == "documents"
        assert body["data"]["attributes"]["filename"] == "contract.pdf"
        assert body["data"]["attributes"]["template"]["data"] == {"name": "John"}
        assert body["data"]["attributes"]["template"]["key"] == "tmpl-456"

    async def test_add_document_from_upload(self):
        client = _mock_client()
        expected = {"data": {"id": "doc-456", "type": "documents"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_document_from_upload",
            [client, "env-123", "contract.pdf", "JVBERi0xLjQK"],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        body = call_args[1]["json"]
        assert body["data"]["attributes"]["content_base64"] == "JVBERi0xLjQK"
        assert body["data"]["attributes"]["filename"] == "contract.pdf"

    async def test_get_document(self):
        client = _mock_client()
        expected = {"data": {"id": "doc-123", "type": "documents"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_get_document", [client, "env-123", "doc-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123/documents/doc-123" in call_args[0][1]

    async def test_list_documents(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_list_documents", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123/documents" in call_args[0][1]

    async def test_update_document(self):
        client = _mock_client()
        expected = {"data": {"id": "doc-123", "type": "documents"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_update_document",
            [client, "env-123", "doc-123", "updated_contract.pdf"],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "PATCH"
        assert "/envelopes/env-123/documents/doc-123" in call_args[0][1]
        body = call_args[1]["json"]
        assert body["data"]["attributes"]["filename"] == "updated_contract.pdf"

    async def test_delete_document(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call(
            "clicksign_delete_document", [client, "env-123", "doc-123"]
        )
        assert result is True


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignSigners:
    async def test_add_signer(self):
        client = _mock_client()
        expected = {"data": {"id": "signer-123", "type": "signers"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_signer",
            [client, "env-123", "John Doe", "john@example.com"],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        body = call_args[1]["json"]
        assert body["data"]["type"] == "signers"
        attrs = body["data"]["attributes"]
        assert attrs["name"] == "John Doe"
        assert attrs["email"] == "john@example.com"
        assert attrs["group"] == 1
        # Optional fields should not be in body when not provided
        assert "phone_number" not in attrs
        assert "documentation" not in attrs
        assert "birthday" not in attrs

    async def test_add_signer_empty_name_raises_error(self):
        with pytest.raises(ValueError, match="name is required"):
            await default_registry.call(
                "clicksign_add_signer",
                [_mock_client(), "env-123", "", "john@example.com"],
            )

    async def test_add_signer_single_word_name_raises_error(self):
        with pytest.raises(ValueError, match="name must have at least 2 words"):
            await default_registry.call(
                "clicksign_add_signer",
                [_mock_client(), "env-123", "John", "john@example.com"],
            )

    async def test_add_signer_empty_email_raises_error(self):
        with pytest.raises(ValueError, match="email is required"):
            await default_registry.call(
                "clicksign_add_signer",
                [_mock_client(), "env-123", "John Doe", ""],
            )

    async def test_get_signer(self):
        client = _mock_client()
        expected = {"data": {"id": "signer-123", "type": "signers"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_get_signer", [client, "env-123", "signer-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123/signers/signer-123" in call_args[0][1]

    async def test_add_signer_with_optional_params(self):
        client = _mock_client()
        expected = {"data": {"id": "signer-456", "type": "signers"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_signer",
            [
                client,
                "env-123",
                "John Doe",
                "john@example.com",
                "+5511999999999",
                "12345678900",
            ],
        )
        assert result == expected

        call_args = client._session.request.call_args
        body = call_args[1]["json"]
        attrs = body["data"]["attributes"]
        assert attrs["phone_number"] == "+5511999999999"
        assert attrs["documentation"] == "12345678900"

    async def test_list_signers(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_list_signers", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123/signers" in call_args[0][1]

    async def test_delete_signer(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call(
            "clicksign_delete_signer", [client, "env-123", "signer-123"]
        )
        assert result is True


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignRequirements:
    async def test_add_qualification(self):
        client = _mock_client()
        expected = {"data": {"id": "req-123", "type": "requirements"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_qualification",
            [client, "env-123", "doc-123", "signer-123", "agree", "sign"],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        body = call_args[1]["json"]
        assert body["data"]["type"] == "requirements"
        assert body["data"]["attributes"]["action"] == "agree"
        assert body["data"]["attributes"]["role"] == "sign"
        rels = body["data"]["relationships"]
        assert rels["document"]["data"]["id"] == "doc-123"
        assert rels["signer"]["data"]["id"] == "signer-123"

    async def test_add_authentication(self):
        client = _mock_client()
        expected = {"data": {"id": "req-456", "type": "requirements"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_add_authentication",
            [client, "env-123", "doc-123", "signer-123", "email"],
        )
        assert result == expected

        call_args = client._session.request.call_args
        body = call_args[1]["json"]
        assert body["data"]["attributes"]["action"] == "provide_evidence"
        assert body["data"]["attributes"]["auth"] == "email"

    async def test_list_requirements(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_list_requirements", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/envelopes/env-123/requirements" in call_args[0][1]

    async def test_delete_requirement(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call(
            "clicksign_delete_requirement", [client, "env-123", "req-123"]
        )
        assert result is True

    async def test_batch_requirements(self):
        client = _mock_client()
        expected = {"data": [{"id": "req-1"}, {"id": "req-2"}]}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        requirements = [
            {
                "action": "agree",
                "role": "sign",
                "document_id": "doc-123",
                "signer_id": "signer-123",
            },
            {
                "action": "provide_evidence",
                "auth": "email",
                "document_id": "doc-123",
                "signer_id": "signer-123",
            },
        ]
        result = await default_registry.call(
            "clicksign_batch_requirements", [client, "env-123", requirements]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/envelopes/env-123/requirements" in call_args[0][1]
        body = call_args[1]["json"]
        assert len(body["data"]) == 2
        assert body["data"][0]["attributes"]["action"] == "agree"
        assert body["data"][1]["attributes"]["action"] == "provide_evidence"


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignNotifications:
    async def test_notify_signer(self):
        client = _mock_client()
        expected = {"data": {"id": "notif-123"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_notify_signer", [client, "env-123", "signer-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/envelopes/env-123/signers/signer-123/notifications" in call_args[0][1]

    async def test_notify_all(self):
        client = _mock_client()
        expected = {"data": {"id": "notif-all"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_notify_all", [client, "env-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/envelopes/env-123/notifications" in call_args[0][1]


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignTemplates:
    async def test_list_templates(self):
        client = _mock_client()
        expected = {"data": [{"id": "tmpl-1"}, {"id": "tmpl-2"}]}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("clicksign_list_templates", [client])
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/templates" in call_args[0][1]

    async def test_get_template(self):
        client = _mock_client()
        expected = {"data": {"id": "tmpl-123", "type": "templates"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call(
            "clicksign_get_template", [client, "tmpl-123"]
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/templates/tmpl-123" in call_args[0][1]


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestClicksignWebhooks:
    async def test_create_webhook(self):
        client = _mock_client()
        expected = {"data": {"id": "wh-123", "type": "webhooks"}}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        events = ["envelope.closed", "signer.signed"]
        result = await default_registry.call(
            "clicksign_create_webhook",
            [client, "https://my-app.com/webhooks", events],
        )
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/webhooks" in call_args[0][1]
        body = call_args[1]["json"]
        assert body["data"]["type"] == "webhooks"
        assert body["data"]["attributes"]["url"] == "https://my-app.com/webhooks"
        assert body["data"]["attributes"]["events"] == events

    async def test_create_webhook_empty_url_raises_error(self):
        with pytest.raises(ValueError, match="url cannot be empty"):
            await default_registry.call(
                "clicksign_create_webhook", [_mock_client(), "", ["envelope.closed"]]
            )

    async def test_create_webhook_empty_events_raises_error(self):
        with pytest.raises(ValueError, match="events cannot be empty"):
            await default_registry.call(
                "clicksign_create_webhook",
                [_mock_client(), "https://example.com/webhook", []],
            )

    async def test_list_webhooks(self):
        client = _mock_client()
        expected = {"data": []}
        client._session.request = MagicMock(return_value=_mock_response(200, expected))

        result = await default_registry.call("clicksign_list_webhooks", [client])
        assert result == expected

        call_args = client._session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/webhooks" in call_args[0][1]

    async def test_delete_webhook(self):
        client = _mock_client()
        client._session.request = MagicMock(return_value=_mock_response(204))

        result = await default_registry.call(
            "clicksign_delete_webhook", [client, "wh-123"]
        )
        assert result is True


# ============================================================================
# Graceful Degradation
# ============================================================================


@pytest.mark.skipif(AIOHTTP_AVAILABLE, reason="Test only when aiohttp is not installed")
class TestClicksignGracefulDegradation:
    def test_opcode_not_registered(self):
        opcodes = default_registry.list_opcodes()
        clicksign_opcodes = [op for op in opcodes if op.startswith("clicksign_")]
        assert clicksign_opcodes == []
