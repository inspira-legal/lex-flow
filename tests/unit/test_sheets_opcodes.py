"""Tests for Google Sheets opcodes."""

import importlib.util
import pytest
from unittest.mock import Mock, patch

from lexflow import default_registry

pytestmark = pytest.mark.asyncio

SHEETS_AVAILABLE = importlib.util.find_spec("googleapiclient") is not None


async def fake_to_thread(func, *args, **kwargs):
    """Convert asyncio.to_thread to sync call for tests."""
    return func(*args, **kwargs)


def create_mock_client():
    """Build a Mock mimicking SheetsClient interface."""
    client = Mock()
    spreadsheets = Mock()
    client.spreadsheets = spreadsheets

    # values() returns a sub-resource with get/update/append/clear
    values = Mock()
    spreadsheets.values.return_value = values

    # spreadsheets.get() and batchUpdate() for management ops
    spreadsheets.get.return_value = Mock()
    spreadsheets.batchUpdate.return_value = Mock()

    return client


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsCreateClient:
    async def test_create_client_with_adc(self):
        mock_creds = Mock()
        with (
            patch("asyncio.to_thread", side_effect=fake_to_thread),
            patch(
                "lexflow.opcodes.opcodes_sheets.google_auth_default",
                return_value=(mock_creds, "project-id"),
            ),
            patch(
                "lexflow.opcodes.opcodes_sheets.build",
                return_value=Mock(),
            ) as mock_build,
        ):
            result = await default_registry.call("sheets_create_client", [])
            mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds)
            assert hasattr(result, "service")
            assert hasattr(result, "spreadsheets")

    async def test_create_client_rejects_non_json_path(self):
        with pytest.raises(ValueError, match="credentials_path must be a .json file"):
            await default_registry.call("sheets_create_client", ["/etc/passwd"])

    async def test_create_client_rejects_path_traversal(self):
        with pytest.raises(ValueError, match="must not contain '..'"):
            await default_registry.call(
                "sheets_create_client", ["../../etc/secrets/creds.json"]
            )

    async def test_create_client_rejects_nonexistent_file(self):
        with pytest.raises(ValueError, match="credentials file not found"):
            await default_registry.call(
                "sheets_create_client", ["/nonexistent/path/creds.json"]
            )

    async def test_create_client_with_service_account(self):
        mock_creds = Mock()
        with (
            patch("asyncio.to_thread", side_effect=fake_to_thread),
            patch("os.path.isfile", return_value=True),
            patch(
                "lexflow.opcodes.opcodes_sheets.Credentials.from_service_account_file",
                return_value=mock_creds,
            ),
            patch(
                "lexflow.opcodes.opcodes_sheets.build",
                return_value=Mock(),
            ) as mock_build,
        ):
            result = await default_registry.call(
                "sheets_create_client", ["/path/to/sa.json"]
            )
            mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds)
            assert hasattr(result, "service")


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsReadOpcodes:
    async def test_get_values_returns_2d_list(self):
        client = create_mock_client()
        expected = [["a", "b"], ["c", "d"]]
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": expected
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_values", [client, "sid", "Sheet1!A1:B2"]
            )
        assert result == expected

    async def test_get_values_empty_range(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_values", [client, "sid", "Sheet1!A1:B2"]
            )
        assert result == []

    async def test_get_row_returns_list(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["x", "y", "z"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_row", [client, "sid", "Sheet1", 5]
            )
        assert result == ["x", "y", "z"]

    async def test_get_row_empty_result(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_row", [client, "sid", "Sheet1", 5]
            )
        assert result == []

    async def test_get_column_returns_flat_list(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"], ["b"], ["c"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_column", [client, "sid", "Sheet1", "A"]
            )
        assert result == ["a", "b", "c"]

    async def test_get_column_empty_rows(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"], [], ["c"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_column", [client, "sid", "Sheet1", "A"]
            )
        assert result == ["a", "", "c"]

    async def test_get_last_row_with_data(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"], ["b"], ["c"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_last_row", [client, "sid", "Sheet1"]
            )
        assert result == 3

    async def test_get_last_row_empty_sheet(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_get_last_row", [client, "sid", "Sheet1"]
            )
        assert result == 0


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsWriteOpcodes:
    async def test_update_returns_summary(self):
        client = create_mock_client()
        client.spreadsheets.values().update.return_value.execute.return_value = {
            "spreadsheetId": "sid",
            "updatedRange": "Sheet1!A1:C1",
            "updatedRows": 1,
            "updatedColumns": 3,
            "updatedCells": 3,
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_update",
                [client, "sid", "Sheet1!A1:C1", [["a", "b", "c"]]],
            )
        assert result["updatedCells"] == 3
        assert result["updatedRows"] == 1

    async def test_update_user_entered_option(self):
        client = create_mock_client()
        client.spreadsheets.values().update.return_value.execute.return_value = {
            "spreadsheetId": "sid",
            "updatedRange": "Sheet1!A1",
            "updatedRows": 1,
            "updatedColumns": 1,
            "updatedCells": 1,
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_update",
                [client, "sid", "Sheet1!A1", [["=SUM(B1:B10)"]], "USER_ENTERED"],
            )
        assert result["updatedCells"] == 1
        # Verify USER_ENTERED was passed
        client.spreadsheets.values().update.assert_called_with(
            spreadsheetId="sid",
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [["=SUM(B1:B10)"]]},
        )

    async def test_append_returns_summary(self):
        client = create_mock_client()
        client.spreadsheets.values().append.return_value.execute.return_value = {
            "updates": {
                "spreadsheetId": "sid",
                "updatedRange": "Sheet1!A4:C4",
                "updatedRows": 1,
                "updatedColumns": 3,
                "updatedCells": 3,
            }
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_append",
                [client, "sid", "Sheet1!A:C", [["Alice", 30, "alice@test.com"]]],
            )
        assert result["updatedCells"] == 3
        assert result["updatedRange"] == "Sheet1!A4:C4"

    async def test_append_insert_rows(self):
        client = create_mock_client()
        client.spreadsheets.values().append.return_value.execute.return_value = {
            "updates": {
                "spreadsheetId": "sid",
                "updatedRange": "Sheet1!A4:C4",
                "updatedRows": 1,
                "updatedColumns": 3,
                "updatedCells": 3,
            }
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call(
                "sheets_append",
                [client, "sid", "Sheet1!A:C", [["row"]]],
            )
        client.spreadsheets.values().append.assert_called_with(
            spreadsheetId="sid",
            range="Sheet1!A:C",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [["row"]]},
        )

    async def test_clear_returns_cleared_range(self):
        client = create_mock_client()
        client.spreadsheets.values().clear.return_value.execute.return_value = {
            "clearedRange": "Sheet1!A2:D100"
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_clear", [client, "sid", "Sheet1!A2:D100"]
            )
        assert result == {"clearedRange": "Sheet1!A2:D100"}


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsManagement:
    async def test_list_sheets_returns_list(self):
        client = create_mock_client()
        client.spreadsheets.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"sheetId": 0, "title": "Sheet1", "index": 0}},
                {"properties": {"sheetId": 123, "title": "Data", "index": 1}},
            ]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call("sheets_list_sheets", [client, "sid"])
        assert len(result) == 2
        assert result[0] == {"sheetId": 0, "title": "Sheet1", "index": 0}
        assert result[1]["title"] == "Data"

    async def test_list_sheets_empty(self):
        client = create_mock_client()
        client.spreadsheets.get.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call("sheets_list_sheets", [client, "sid"])
        assert result == []

    async def test_create_sheet_returns_id_and_title(self):
        client = create_mock_client()
        client.spreadsheets.batchUpdate.return_value.execute.return_value = {
            "replies": [
                {"addSheet": {"properties": {"sheetId": 999, "title": "New Tab"}}}
            ]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_create_sheet", [client, "sid", "New Tab"]
            )
        assert result == {"sheetId": 999, "title": "New Tab"}

    async def test_create_sheet_empty_replies(self):
        client = create_mock_client()
        client.spreadsheets.batchUpdate.return_value.execute.return_value = {
            "replies": []
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_create_sheet", [client, "sid", "X"]
            )
        assert result == {}

    async def test_delete_sheet_returns_success(self):
        client = create_mock_client()
        client.spreadsheets.batchUpdate.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_delete_sheet", [client, "sid", 999]
            )
        assert result == {"deleted": True, "sheetId": 999}


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsUtility:
    async def test_test_connection_returns_true(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {}
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            result = await default_registry.call(
                "sheets_test_connection", [client, "sid"]
            )
        assert result is True

    async def test_test_connection_propagates_exception(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.side_effect = Exception(
            "403 Forbidden"
        )
        with (
            patch("asyncio.to_thread", side_effect=fake_to_thread),
            pytest.raises(Exception, match="403 Forbidden"),
        ):
            await default_registry.call("sheets_test_connection", [client, "sid"])


@pytest.mark.skipif(
    not SHEETS_AVAILABLE, reason="google-api-python-client not installed"
)
class TestSheetsSheetNameQuoting:
    """Verify sheet names with spaces/special chars are quoted in A1 ranges."""

    async def test_get_row_quotes_sheet_name_with_spaces(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a", "b"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call(
                "sheets_get_row", [client, "sid", "My Sheet", 5]
            )
        client.spreadsheets.values().get.assert_called_with(
            spreadsheetId="sid", range="'My Sheet'!5:5"
        )

    async def test_get_column_quotes_sheet_name_with_spaces(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call(
                "sheets_get_column", [client, "sid", "My Sheet", "A"]
            )
        client.spreadsheets.values().get.assert_called_with(
            spreadsheetId="sid", range="'My Sheet'!A:A"
        )

    async def test_get_last_row_quotes_sheet_name_with_spaces(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call(
                "sheets_get_last_row", [client, "sid", "My Sheet"]
            )
        client.spreadsheets.values().get.assert_called_with(
            spreadsheetId="sid", range="'My Sheet'"
        )

    async def test_sheet_name_with_single_quotes_escaped(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call(
                "sheets_get_row", [client, "sid", "John's Data", 1]
            )
        client.spreadsheets.values().get.assert_called_with(
            spreadsheetId="sid", range="'John''s Data'!1:1"
        )

    async def test_simple_sheet_name_not_quoted(self):
        client = create_mock_client()
        client.spreadsheets.values().get.return_value.execute.return_value = {
            "values": [["a"]]
        }
        with patch("asyncio.to_thread", side_effect=fake_to_thread):
            await default_registry.call("sheets_get_row", [client, "sid", "Sheet1", 1])
        client.spreadsheets.values().get.assert_called_with(
            spreadsheetId="sid", range="Sheet1!1:1"
        )


@pytest.mark.skipif(SHEETS_AVAILABLE, reason="google-api-python-client IS installed")
async def test_sheets_opcodes_not_registered_when_not_installed():
    """L1: Graceful degradation when google-api-python-client is not installed."""
    opcodes = default_registry.list_opcodes()
    sheets_opcodes = [op for op in opcodes if op.startswith("sheets_")]
    assert sheets_opcodes == []
