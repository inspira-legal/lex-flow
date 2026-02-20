"""Google Sheets opcodes for LexFlow.

This module provides opcodes for interacting with Google Sheets API,
enabling spreadsheet automation workflows similar to n8n/Zapier.

Installation:
    pip install lexflow[sheets]
    or:
    pip install google-auth google-auth-oauthlib google-api-python-client

Authentication:
    Option 1 - Service Account (recommended for production):
        Pass path to service account JSON file to sheets_create_client()

    Option 2 - Application Default Credentials (recommended for development):
        Run: gcloud auth application-default login
        Then call sheets_create_client() without arguments
"""

import asyncio
from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    from google.oauth2.service_account import Credentials
    from google.auth import default as google_auth_default
    from googleapiclient.discovery import build

    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsClient:
    """Reusable Google Sheets client."""

    def __init__(self, service):
        self.service = service
        self.spreadsheets = service.spreadsheets()


def register_sheets_opcodes():
    """Register Google Sheets opcodes to the default registry."""
    if not SHEETS_AVAILABLE:
        return

    register_category(
        id="sheets",
        label="Google Sheets Operations",
        prefix="sheets_",
        color="#34A853",
        icon="📊",
        requires="sheets",
        order=210,
    )

    # ============================================================================
    # Authentication
    # ============================================================================

    @opcode(category="sheets")
    async def sheets_create_client(
        credentials_path: Optional[str] = None,
    ) -> SheetsClient:
        """Create a Google Sheets client for API operations.

        Args:
            credentials_path: Path to service account JSON file. If None,
                uses Application Default Credentials (ADC).

        Returns:
            SheetsClient object to use with other sheets_* opcodes

        Example with Service Account:
            credentials_path: "/path/to/service-account.json"

        Example with ADC (after running 'gcloud auth application-default login'):
            # No arguments needed
        """
        if credentials_path:
            credentials = await asyncio.to_thread(
                Credentials.from_service_account_file, credentials_path, scopes=SCOPES
            )
        else:
            credentials, _ = await asyncio.to_thread(google_auth_default, scopes=SCOPES)

        service = await asyncio.to_thread(
            build, "sheets", "v4", credentials=credentials
        )
        return SheetsClient(service)

    # ============================================================================
    # Read Operations
    # ============================================================================

    @opcode(category="sheets")
    async def sheets_get_values(
        client: SheetsClient,
        spreadsheet_id: str,
        range_notation: str,
    ) -> List[List[Any]]:
        """Read values from a Google Sheet range.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            range_notation: Range in A1 notation (e.g., "Sheet1!A1:D10")

        Returns:
            2D list of values (rows x columns). Empty cells are empty strings.

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            range_notation: "Sheet1!A1:D10"
        """
        request = client.spreadsheets.values().get(
            spreadsheetId=spreadsheet_id, range=range_notation
        )
        result = await asyncio.to_thread(request.execute)
        return result.get("values", [])

    @opcode(category="sheets")
    async def sheets_get_row(
        client: SheetsClient,
        spreadsheet_id: str,
        sheet_name: str,
        row_number: int,
    ) -> List[Any]:
        """Read a specific row from a Google Sheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            sheet_name: Name of the sheet (tab)
            row_number: Row number (1-indexed)

        Returns:
            List of values in the row

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sheet_name: "Sheet1"
            row_number: 5
        """
        range_notation = f"{sheet_name}!{row_number}:{row_number}"
        request = client.spreadsheets.values().get(
            spreadsheetId=spreadsheet_id, range=range_notation
        )
        result = await asyncio.to_thread(request.execute)
        values = result.get("values", [])
        return values[0] if values else []

    @opcode(category="sheets")
    async def sheets_get_column(
        client: SheetsClient,
        spreadsheet_id: str,
        sheet_name: str,
        column: str,
    ) -> List[Any]:
        """Read a specific column from a Google Sheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            sheet_name: Name of the sheet (tab)
            column: Column letter (e.g., "A", "B", "AA")

        Returns:
            List of values in the column (excluding empty trailing cells)

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sheet_name: "Sheet1"
            column: "A"
        """
        range_notation = f"{sheet_name}!{column}:{column}"
        request = client.spreadsheets.values().get(
            spreadsheetId=spreadsheet_id, range=range_notation
        )
        result = await asyncio.to_thread(request.execute)
        values = result.get("values", [])
        return [row[0] if row else "" for row in values]

    @opcode(category="sheets")
    async def sheets_get_last_row(
        client: SheetsClient,
        spreadsheet_id: str,
        sheet_name: str,
    ) -> int:
        """Get the number of the last row with data in a sheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            sheet_name: Name of the sheet (tab)

        Returns:
            Last row number with data (0 if sheet is empty)

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sheet_name: "Sheet1"
        """
        request = client.spreadsheets.values().get(
            spreadsheetId=spreadsheet_id, range=sheet_name
        )
        result = await asyncio.to_thread(request.execute)
        values = result.get("values", [])
        return len(values)

    # ============================================================================
    # Write Operations
    # ============================================================================

    @opcode(category="sheets")
    async def sheets_update(
        client: SheetsClient,
        spreadsheet_id: str,
        range_notation: str,
        values: List[List[Any]],
        value_input_option: str = "RAW",
    ) -> Dict[str, Any]:
        """Update values in a Google Sheet range.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            range_notation: Range in A1 notation (e.g., "Sheet1!A1:D10")
            values: 2D list of values (rows x columns)
            value_input_option: "RAW" for raw values, "USER_ENTERED" for formulas

        Returns:
            Response dict with updatedCells, updatedRows, updatedColumns

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            range_notation: "Sheet1!A1:C1"
            values: [["Name", "Age", "Email"]]
        """
        request = client.spreadsheets.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_notation,
            valueInputOption=value_input_option,
            body={"values": values},
        )
        result = await asyncio.to_thread(request.execute)
        return {
            "spreadsheetId": result.get("spreadsheetId"),
            "updatedRange": result.get("updatedRange"),
            "updatedRows": result.get("updatedRows"),
            "updatedColumns": result.get("updatedColumns"),
            "updatedCells": result.get("updatedCells"),
        }

    @opcode(category="sheets")
    async def sheets_append(
        client: SheetsClient,
        spreadsheet_id: str,
        range_notation: str,
        values: List[List[Any]],
        value_input_option: str = "RAW",
    ) -> Dict[str, Any]:
        """Append rows to a Google Sheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            range_notation: Range to append after (e.g., "Sheet1!A:D")
            values: 2D list of values to append (each inner list is a row)
            value_input_option: "RAW" for raw values, "USER_ENTERED" for formulas

        Returns:
            Response dict with updatedCells, updatedRows, updatedRange

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            range_notation: "Sheet1!A:C"
            values: [["Alice", 30, "alice@example.com"]]
        """
        request = client.spreadsheets.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_notation,
            valueInputOption=value_input_option,
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        )
        result = await asyncio.to_thread(request.execute)
        updates = result.get("updates", {})
        return {
            "spreadsheetId": updates.get("spreadsheetId"),
            "updatedRange": updates.get("updatedRange"),
            "updatedRows": updates.get("updatedRows"),
            "updatedColumns": updates.get("updatedColumns"),
            "updatedCells": updates.get("updatedCells"),
        }

    @opcode(category="sheets")
    async def sheets_clear(
        client: SheetsClient,
        spreadsheet_id: str,
        range_notation: str,
    ) -> Dict[str, Any]:
        """Clear values from a Google Sheet range.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            range_notation: Range in A1 notation to clear (e.g., "Sheet1!A1:D10")

        Returns:
            Response dict with clearedRange

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            range_notation: "Sheet1!A2:D100"
        """
        request = client.spreadsheets.values().clear(
            spreadsheetId=spreadsheet_id, range=range_notation, body={}
        )
        result = await asyncio.to_thread(request.execute)
        return {"clearedRange": result.get("clearedRange")}

    # ============================================================================
    # Sheet Management
    # ============================================================================

    @opcode(category="sheets")
    async def sheets_list_sheets(
        client: SheetsClient,
        spreadsheet_id: str,
    ) -> List[Dict[str, Any]]:
        """List all sheets (tabs) in a spreadsheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)

        Returns:
            List of dicts with sheetId, title, index for each sheet

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        request = client.spreadsheets.get(spreadsheetId=spreadsheet_id)
        result = await asyncio.to_thread(request.execute)
        sheets = result.get("sheets", [])
        return [
            {
                "sheetId": sheet["properties"]["sheetId"],
                "title": sheet["properties"]["title"],
                "index": sheet["properties"]["index"],
            }
            for sheet in sheets
        ]

    @opcode(category="sheets")
    async def sheets_create_sheet(
        client: SheetsClient,
        spreadsheet_id: str,
        title: str,
    ) -> Dict[str, Any]:
        """Create a new sheet (tab) in a spreadsheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            title: Name for the new sheet

        Returns:
            Dict with sheetId and title of the created sheet

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            title: "New Sheet"
        """
        request_body = {"requests": [{"addSheet": {"properties": {"title": title}}}]}
        request = client.spreadsheets.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        )
        result = await asyncio.to_thread(request.execute)
        replies = result.get("replies", [])
        if replies and "addSheet" in replies[0]:
            props = replies[0]["addSheet"]["properties"]
            return {"sheetId": props["sheetId"], "title": props["title"]}
        return {}

    @opcode(category="sheets")
    async def sheets_delete_sheet(
        client: SheetsClient,
        spreadsheet_id: str,
        sheet_id: int,
    ) -> Dict[str, Any]:
        """Delete a sheet (tab) from a spreadsheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            sheet_id: The sheet ID to delete (from sheets_list_sheets)

        Returns:
            Dict with success status

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            sheet_id: 123456789
        """
        request_body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
        request = client.spreadsheets.batchUpdate(
            spreadsheetId=spreadsheet_id, body=request_body
        )
        await asyncio.to_thread(request.execute)
        return {"deleted": True, "sheetId": sheet_id}

    # ============================================================================
    # Utility
    # ============================================================================

    @opcode(category="sheets")
    async def sheets_test_connection(
        client: SheetsClient,
        spreadsheet_id: str,
        range_notation: str = "A1:B2",
    ) -> bool:
        """Test connection to a Google Sheet.

        Args:
            client: SheetsClient from sheets_create_client
            spreadsheet_id: The spreadsheet ID (from URL)
            range_notation: Range to test reading (default: "A1:B2")

        Returns:
            True if connection successful, raises exception otherwise

        Example:
            client: { node: create_client }
            spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        request = client.spreadsheets.values().get(
            spreadsheetId=spreadsheet_id, range=range_notation
        )
        await asyncio.to_thread(request.execute)
        return True
