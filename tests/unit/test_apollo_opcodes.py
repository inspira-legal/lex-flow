"""Tests for Apollo.io opcodes."""

import importlib.util
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from lexflow import default_registry


AIOHTTP_AVAILABLE = importlib.util.find_spec("aiohttp") is not None

try:
    from lexflow.opcodes.opcodes_apollo import (
        _build_query_params,
        _build_excluded_brazilian_states,
        _check_aiohttp,
        ApolloClient,
        APOLLO_AVAILABLE,
        BRAZILIAN_STATES,
        DEFAULT_LEGAL_INDUSTRIES,
        DEFAULT_LEGAL_KEYWORDS,
        DEFAULT_LEGAL_SIC_CODES,
        DEFAULT_LEGAL_TITLES,
    )

    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False


# =============================================================================
# Helper functions
# =============================================================================


class TestCheckAiohttp:
    """Tests for _check_aiohttp helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_raises_import_error_when_not_installed(self):
        with patch("lexflow.opcodes.opcodes_apollo.APOLLO_AVAILABLE", False):
            with pytest.raises(ImportError, match="aiohttp is required"):
                _check_aiohttp()

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    @pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
    def test_no_error_when_installed(self):
        _check_aiohttp()


class TestBuildQueryParams:
    """Tests for _build_query_params helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_scalar_values(self):
        result = _build_query_params({"page": 1, "per_page": 100})
        assert ("page", "1") in result
        assert ("per_page", "100") in result

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_list_values_expanded_with_brackets(self):
        result = _build_query_params({"ids": ["a", "b"]})
        assert ("ids[]", "a") in result
        assert ("ids[]", "b") in result

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_none_values_skipped(self):
        result = _build_query_params({"a": "yes", "b": None})
        assert len(result) == 1
        assert ("a", "yes") in result

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_empty_dict(self):
        assert _build_query_params({}) == []

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_mixed_scalars_and_lists(self):
        result = _build_query_params({
            "page": 1,
            "organization_ids": ["org1", "org2"],
            "skip": None,
        })
        assert len(result) == 3
        assert ("page", "1") in result
        assert ("organization_ids[]", "org1") in result
        assert ("organization_ids[]", "org2") in result


class TestBuildExcludedBrazilianStates:
    """Tests for _build_excluded_brazilian_states helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_excludes_non_selected_states(self):
        excluded = _build_excluded_brazilian_states(["são paulo, Brazil"])
        assert "são paulo" not in excluded
        assert "rio de janeiro" in excluded
        assert len(excluded) == len(BRAZILIAN_STATES) - 1

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_multiple_selected_states(self):
        excluded = _build_excluded_brazilian_states([
            "são paulo, Brazil",
            "rio de janeiro, Brazil",
        ])
        assert "são paulo" not in excluded
        assert "rio de janeiro" not in excluded
        assert len(excluded) == len(BRAZILIAN_STATES) - 2

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_no_match_returns_empty(self):
        excluded = _build_excluded_brazilian_states(["New York, USA"])
        assert excluded == []

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_case_insensitive(self):
        excluded = _build_excluded_brazilian_states(["São Paulo, Brazil"])
        assert "são paulo" not in excluded
        assert len(excluded) == len(BRAZILIAN_STATES) - 1


# =============================================================================
# Constants
# =============================================================================


class TestConstants:
    """Tests for legal industry constants."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_keywords_count(self):
        assert len(DEFAULT_LEGAL_KEYWORDS) == 150

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_keywords_no_duplicates(self):
        assert len(DEFAULT_LEGAL_KEYWORDS) == len(set(DEFAULT_LEGAL_KEYWORDS))

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_titles_count(self):
        assert len(DEFAULT_LEGAL_TITLES) == 51

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_titles_no_duplicates(self):
        assert len(DEFAULT_LEGAL_TITLES) == len(set(DEFAULT_LEGAL_TITLES))

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_brazilian_states_count(self):
        assert len(BRAZILIAN_STATES) == 27

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_default_industries(self):
        assert DEFAULT_LEGAL_INDUSTRIES == ["law practice", "legal services"]

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_default_sic_codes(self):
        assert DEFAULT_LEGAL_SIC_CODES == ["8111"]


# =============================================================================
# Client
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestApolloClient:
    """Tests for ApolloClient."""

    pytestmark = pytest.mark.asyncio

    async def test_create_client(self):
        result = await default_registry.call("apollo_create_client", ["test-key"])
        assert isinstance(result, ApolloClient)
        assert result.api_key == "test-key"
        await result._session.close()

    async def test_empty_key_raises_error(self):
        with pytest.raises(ValueError, match="api_key is required"):
            await default_registry.call("apollo_create_client", [""])

    async def test_repr_masks_key(self):
        result = await default_registry.call("apollo_create_client", ["secret-key"])
        assert repr(result) == "ApolloClient(api_key=***)"
        assert "secret-key" not in repr(result)
        await result._session.close()

    async def test_close_client(self):
        client = await default_registry.call("apollo_create_client", ["test-key"])
        result = await default_registry.call("apollo_close_client", [client])
        assert result is True

    async def test_context_manager(self):
        client = ApolloClient("test-key")
        async with client as c:
            assert c is client
        assert client._session.closed


# =============================================================================
# Search Companies
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestSearchCompanies:
    """Tests for apollo_search_companies opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_search(self):
        mock_response = {
            "model_ids": ["org1", "org2"],
            "organizations": [{"id": "org1", "name": "Test Corp"}],
            "breadcrumbs": [],
        }

        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value=mock_response)

        # apollo_search_companies(client, organization_locations, ...)
        result = await default_registry.call(
            "apollo_search_companies",
            [client, ["Brazil"]],
        )

        assert result["model_ids"] == ["org1", "org2"]
        client.post.assert_called_once()
        call_kwargs = client.post.call_args
        body = call_kwargs[1]["json_data"]
        assert body["organization_locations"] == ["Brazil"]
        assert body["per_page"] == 100
        assert body["page"] == 1

    async def test_all_filters(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": [], "organizations": []})

        # Positional: client, locations, not_locations, employee_ranges,
        #   industries, keyword_tags, sic_codes, tech_uids, org_ids,
        #   org_name, revenue_min, revenue_max
        await default_registry.call(
            "apollo_search_companies",
            [
                client,
                ["Brazil"],           # organization_locations
                ["acre"],             # organization_not_locations
                ["1,10"],             # organization_num_employees_ranges
                ["legal services"],   # organization_industries
                ["law firm"],         # q_organization_keyword_tags
                ["8111"],             # q_organization_sic_codes
                None,                 # currently_using_any_of_technology_uids
                None,                 # organization_ids
                ["Test"],             # q_organization_name
                1000,                 # revenue_range_min
                50000,                # revenue_range_max
            ],
        )

        body = client.post.call_args[1]["json_data"]
        assert body["organization_locations"] == ["Brazil"]
        assert body["organization_not_locations"] == ["acre"]
        assert body["organization_num_employees_ranges"] == ["1,10"]
        assert body["organization_industries"] == ["legal services"]
        assert body["q_organization_keyword_tags"] == ["law firm"]
        assert body["q_organization_sic_codes"] == ["8111"]
        assert body["q_organization_name"] == ["Test"]
        assert body["revenue[min]"] == 1000
        assert body["revenue[max]"] == 50000

    async def test_optional_params_excluded_when_none(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": []})

        await default_registry.call("apollo_search_companies", [client])

        body = client.post.call_args[1]["json_data"]
        assert "organization_locations" not in body
        assert "organization_industries" not in body
        assert body == {"per_page": 100, "page": 1}


# =============================================================================
# Search People
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestSearchPeople:
    """Tests for apollo_search_people opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_search(self):
        mock_response = {
            "people": [{"id": "p1", "first_name": "John", "title": "Partner"}]
        }

        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value=mock_response)

        # apollo_search_people(client, organization_ids, ...)
        result = await default_registry.call(
            "apollo_search_people",
            [client, ["org1"]],
        )

        assert result["people"][0]["first_name"] == "John"
        call_args = client.post.call_args
        assert call_args[1]["params"] is not None

    async def test_uses_query_params_not_body(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"people": []})

        # apollo_search_people(client, organization_ids, person_titles, ...)
        await default_registry.call(
            "apollo_search_people",
            [client, ["org1"], ["Partner"]],
        )

        call_args = client.post.call_args
        # Should use params, not json_data
        assert call_args[1].get("json_data") is None
        params = call_args[1]["params"]
        assert ("organization_ids[]", "org1") in params
        assert ("person_titles[]", "Partner") in params

    async def test_endpoint_path(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"people": []})

        await default_registry.call("apollo_search_people", [client])

        endpoint = client.post.call_args[0][0]
        assert endpoint == "/v1/mixed_people/api_search"


# =============================================================================
# Enrich People
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestEnrichPeople:
    """Tests for apollo_enrich_people opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_enrichment(self):
        mock_response = {
            "matches": [
                {"id": "p1", "first_name": "John", "email": "john@test.com"},
                {"id": "p2", "first_name": "Jane", "email": "jane@test.com"},
            ]
        }

        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value=mock_response)

        result = await default_registry.call(
            "apollo_enrich_people",
            [client, ["p1", "p2"]],
        )

        assert len(result) == 2
        assert result[0]["first_name"] == "John"

    async def test_empty_ids_returns_empty(self):
        client = ApolloClient("test-key")

        result = await default_registry.call(
            "apollo_enrich_people",
            [client, []],
        )

        assert result == []

    async def test_chunking(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"matches": [{"id": "p"}]})

        ids = [f"p{i}" for i in range(25)]
        result = await default_registry.call(
            "apollo_enrich_people",
            [client, ids],
        )

        # 25 ids / 10 per chunk = 3 chunks
        assert client.post.call_count == 3
        assert len(result) == 3  # 1 match per chunk

    async def test_chunk_size_capped_at_10(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"matches": [{"id": "p"}]})

        ids = [f"p{i}" for i in range(15)]
        await default_registry.call(
            "apollo_enrich_people",
            [client, ids, True, 50],  # chunk_size=50 should be capped to 10
        )

        assert client.post.call_count == 2  # 15/10 = 2 chunks

    async def test_skips_none_matches(self):
        mock_response = {"matches": [{"id": "p1"}, None, {"id": "p3"}]}

        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value=mock_response)

        result = await default_registry.call(
            "apollo_enrich_people",
            [client, ["p1", "p2", "p3"]],
        )

        assert len(result) == 2

    async def test_failed_chunk_continues(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(
            side_effect=[
                ValueError("API error"),
                {"matches": [{"id": "p11"}]},
            ]
        )

        ids = [f"p{i}" for i in range(15)]
        result = await default_registry.call(
            "apollo_enrich_people",
            [client, ids],
        )

        # First chunk fails, second succeeds
        assert len(result) == 1
        assert result[0]["id"] == "p11"

    async def test_reveal_personal_emails_param(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"matches": []})

        await default_registry.call(
            "apollo_enrich_people",
            [client, ["p1"]],
        )

        params = client.post.call_args[1]["params"]
        assert params == {"reveal_personal_emails": "true"}


# =============================================================================
# Convenience: Search Law Firms
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestSearchLawFirms:
    """Tests for apollo_search_law_firms convenience opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_injects_legal_defaults(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": [], "organizations": []})

        await default_registry.call(
            "apollo_search_law_firms",
            [client, ["são paulo, Brazil"]],
        )

        body = client.post.call_args[1]["json_data"]
        assert body["organization_industries"] == DEFAULT_LEGAL_INDUSTRIES
        assert body["q_organization_keyword_tags"] == DEFAULT_LEGAL_KEYWORDS
        assert body["q_organization_sic_codes"] == DEFAULT_LEGAL_SIC_CODES

    async def test_auto_excludes_brazilian_states(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": [], "organizations": []})

        await default_registry.call(
            "apollo_search_law_firms",
            [client, ["são paulo, Brazil"]],
        )

        body = client.post.call_args[1]["json_data"]
        not_locs = body["organization_not_locations"]
        assert "são paulo" not in not_locs
        assert "rio de janeiro" in not_locs

    async def test_no_exclusion_for_non_br_locations(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": [], "organizations": []})

        await default_registry.call(
            "apollo_search_law_firms",
            [client, ["New York, USA"]],
        )

        body = client.post.call_args[1]["json_data"]
        assert "organization_not_locations" not in body

    async def test_allows_override_defaults(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"model_ids": [], "organizations": []})

        custom_keywords = ["custom keyword"]
        custom_industries = ["tech"]

        # apollo_search_law_firms(client, locations, employee_ranges,
        #   keyword_tags, industries, ...)
        await default_registry.call(
            "apollo_search_law_firms",
            [client, ["Brazil"], None, custom_keywords, custom_industries],
        )

        body = client.post.call_args[1]["json_data"]
        assert body["q_organization_keyword_tags"] == custom_keywords
        assert body["organization_industries"] == custom_industries


# =============================================================================
# Convenience: Search Legal People
# =============================================================================


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
class TestSearchLegalPeople:
    """Tests for apollo_search_legal_people convenience opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_injects_legal_titles_and_verified_email(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"people": []})

        await default_registry.call(
            "apollo_search_legal_people",
            [client, ["org1"]],
        )

        params = client.post.call_args[1]["params"]
        # Check titles are injected
        title_params = [v for k, v in params if k == "person_titles[]"]
        assert len(title_params) == len(DEFAULT_LEGAL_TITLES)
        assert "Sócio" in title_params
        assert "Partner" in title_params

        # Check verified email status
        email_params = [v for k, v in params if k == "contact_email_status[]"]
        assert email_params == ["verified"]

    async def test_allows_override_titles(self):
        client = ApolloClient("test-key")
        client.post = AsyncMock(return_value={"people": []})

        custom_titles = ["CEO", "CTO"]

        # apollo_search_legal_people(client, organization_ids,
        #   person_locations, titles, ...)
        await default_registry.call(
            "apollo_search_legal_people",
            [client, ["org1"], None, custom_titles],
        )

        params = client.post.call_args[1]["params"]
        title_params = [v for k, v in params if k == "person_titles[]"]
        assert title_params == ["CEO", "CTO"]


# =============================================================================
# Registration
# =============================================================================


class TestOpcodeRegistration:
    """Tests for opcode registration."""

    @pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed")
    def test_all_opcodes_registered(self):
        expected = [
            "apollo_create_client",
            "apollo_close_client",
            "apollo_search_companies",
            "apollo_search_people",
            "apollo_enrich_people",
            "apollo_search_law_firms",
            "apollo_search_legal_people",
        ]
        for name in expected:
            assert name in default_registry.opcodes, f"{name} not registered"


@pytest.mark.skipif(AIOHTTP_AVAILABLE, reason="Test only when aiohttp is not installed")
class TestImportErrorWhenNotInstalled:
    """Tests for graceful handling when aiohttp is not installed."""

    def test_opcodes_not_registered(self):
        assert "apollo_create_client" not in default_registry.opcodes
        assert "apollo_search_law_firms" not in default_registry.opcodes
