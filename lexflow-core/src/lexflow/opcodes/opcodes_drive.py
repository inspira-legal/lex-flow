"""Google Drive opcodes for LexFlow.

This module provides opcodes for interacting with Google Drive API,
enabling document reading, file listing, and content extraction workflows.
Designed for use cases like reading meeting transcriptions, accessing shared
documents, and automating document-based pipelines.

Installation:
    pip install lexflow[drive]
    or:
    pip install google-auth google-auth-oauthlib google-api-python-client

Authentication:
    Option 1 - Service Account (recommended for production):
        Pass path to service account JSON file to drive_create_client().
        The service account must have the Drive files shared with it.

    Option 2 - Application Default Credentials (recommended for development):
        Run: gcloud auth application-default login
        Then call drive_create_client() without arguments.
"""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource

try:
    from google.oauth2.service_account import Credentials
    from google.auth import default as google_auth_default
    from googleapiclient.discovery import build

    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]

# MIME types for Google Workspace documents
MIME_GOOGLE_DOC = "application/vnd.google-apps.document"
MIME_GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
MIME_GOOGLE_FOLDER = "application/vnd.google-apps.folder"

# Export MIME types
EXPORT_PLAIN_TEXT = "text/plain"
EXPORT_PDF = "application/pdf"


def register_drive_opcodes():
    """Register Google Drive opcodes to the default registry."""
    if not DRIVE_AVAILABLE:
        return

    from .opcodes import opcode, register_category

    class DriveClient:
        """Reusable Google Drive API client."""

        def __init__(self, service: Resource):
            self.service = service
            self.files = service.files()

    register_category(
        id="drive",
        label="Google Drive",
        prefix="drive_",
        color="#4285F4",
        icon="📁",
        requires="drive",
        order=215,
    )

    # ============================================================================
    # Authentication
    # ============================================================================

    @opcode(category="drive")
    async def drive_create_client(
        credentials_path: Optional[str] = None,
    ) -> DriveClient:
        """Create a Google Drive client for API operations.

        Args:
            credentials_path: Path to service account JSON file. If None,
                uses Application Default Credentials (ADC).

        Returns:
            DriveClient object to use with other drive_* opcodes.

        Example with Service Account:
            credentials_path: "/path/to/service-account.json"

        Example with ADC (after running 'gcloud auth application-default login'):
            # No arguments needed

        Note:
            For service accounts, the Drive files or folders must be explicitly
            shared with the service account email address.
        """
        if credentials_path:
            if ".." in os.path.normpath(credentials_path).split(os.sep):
                raise ValueError(
                    "credentials_path must not contain '..' path components"
                )
            resolved = os.path.realpath(credentials_path)
            if not resolved.endswith(".json"):
                raise ValueError("credentials_path must be a .json file")
            if not os.path.isfile(resolved):
                raise ValueError(f"credentials file not found: {credentials_path}")
            credentials = await asyncio.to_thread(
                Credentials.from_service_account_file, resolved, scopes=SCOPES
            )
        else:
            credentials, _ = await asyncio.to_thread(google_auth_default, scopes=SCOPES)

        service = await asyncio.to_thread(
            build, "drive", "v3", credentials=credentials
        )
        return DriveClient(service)

    # ============================================================================
    # File Discovery
    # ============================================================================

    @opcode(category="drive")
    async def drive_list_files(
        client: DriveClient,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """List files in Google Drive, optionally filtered by folder or query.

        Args:
            client: DriveClient from drive_create_client.
            folder_id: ID of the folder to list files from. If None, lists
                all accessible files.
            query: Additional Drive query string (e.g., "name contains 'reunião'").
            max_results: Maximum number of files to return (default: 100).

        Returns:
            List of file dicts, each with id, name, mimeType, modifiedTime,
            size, and webViewLink.

        Example:
            client: { node: create_client }
            folder_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            query: "name contains 'transcrição'"
        """
        q_parts = ["trashed = false"]
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        if query:
            q_parts.append(query)
        q = " and ".join(q_parts)

        request = client.files.list(
            q=q,
            pageSize=min(max_results, 1000),
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
        )
        result = await asyncio.to_thread(request.execute)
        return result.get("files", [])

    @opcode(category="drive")
    async def drive_search_files(
        client: DriveClient,
        name_contains: str,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search for files in Google Drive by name.

        Args:
            client: DriveClient from drive_create_client.
            name_contains: Text to search for in file names.
            folder_id: Restrict search to a specific folder ID.
            mime_type: Filter by MIME type (e.g., "application/vnd.google-apps.document").
            max_results: Maximum number of files to return (default: 50).

        Returns:
            List of file dicts with id, name, mimeType, modifiedTime, webViewLink.

        Example:
            client: { node: create_client }
            name_contains: "transcrição reunião"
            mime_type: "application/vnd.google-apps.document"
        """
        q_parts = [f"name contains '{name_contains}'", "trashed = false"]
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        if mime_type:
            q_parts.append(f"mimeType = '{mime_type}'")
        q = " and ".join(q_parts)

        request = client.files.list(
            q=q,
            pageSize=min(max_results, 1000),
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc",
        )
        result = await asyncio.to_thread(request.execute)
        return result.get("files", [])

    @opcode(category="drive")
    async def drive_get_file_metadata(
        client: DriveClient,
        file_id: str,
    ) -> Dict[str, Any]:
        """Get metadata for a specific file in Google Drive.

        Args:
            client: DriveClient from drive_create_client.
            file_id: The file ID (from the Drive URL or drive_list_files).

        Returns:
            Dict with id, name, mimeType, modifiedTime, size, webViewLink,
            and parents.

        Example:
            client: { node: create_client }
            file_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        request = client.files.get(
            fileId=file_id,
            fields="id, name, mimeType, modifiedTime, size, webViewLink, parents",
        )
        return await asyncio.to_thread(request.execute)

    # ============================================================================
    # Document Reading
    # ============================================================================

    @opcode(category="drive")
    async def drive_read_document(
        client: DriveClient,
        file_id: str,
    ) -> str:
        """Read a Google Docs document as plain text.

        Ideal for reading meeting transcriptions, notes, and other text documents
        stored as Google Docs.

        Args:
            client: DriveClient from drive_create_client.
            file_id: The Google Doc file ID (from the Drive URL).

        Returns:
            Full document content as plain text string.

        Example:
            client: { node: create_client }
            file_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

        Note:
            Only works with Google Docs (mimeType: application/vnd.google-apps.document).
            For other file types, use drive_download_file_as_string instead.
        """
        request = client.files.export_media(
            fileId=file_id,
            mimeType=EXPORT_PLAIN_TEXT,
        )
        content = await asyncio.to_thread(request.execute)
        if isinstance(content, bytes):
            return content.decode("utf-8")
        return content

    @opcode(category="drive")
    async def drive_download_file_as_string(
        client: DriveClient,
        file_id: str,
        encoding: str = "utf-8",
    ) -> str:
        """Download a file from Google Drive and return its content as text.

        Use for plain text files (.txt, .csv, .md, etc.). For Google Docs,
        use drive_read_document instead.

        Args:
            client: DriveClient from drive_create_client.
            file_id: The file ID to download.
            encoding: Text encoding to decode the file (default: utf-8).

        Returns:
            File content as a string.

        Example:
            client: { node: create_client }
            file_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            encoding: "utf-8"
        """
        request = client.files.get_media(fileId=file_id)
        content = await asyncio.to_thread(request.execute)
        if isinstance(content, bytes):
            return content.decode(encoding)
        return content

    @opcode(category="drive")
    async def drive_download_file_as_bytes(
        client: DriveClient,
        file_id: str,
    ) -> bytes:
        """Download a file from Google Drive as raw bytes.

        Args:
            client: DriveClient from drive_create_client.
            file_id: The file ID to download.

        Returns:
            File content as bytes.

        Example:
            client: { node: create_client }
            file_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        request = client.files.get_media(fileId=file_id)
        content = await asyncio.to_thread(request.execute)
        if isinstance(content, str):
            return content.encode("utf-8")
        return content

    @opcode(category="drive")
    async def drive_export_document_as_pdf(
        client: DriveClient,
        file_id: str,
    ) -> bytes:
        """Export a Google Workspace document (Docs, Sheets, Slides) as PDF.

        Args:
            client: DriveClient from drive_create_client.
            file_id: The Google Workspace file ID to export.

        Returns:
            PDF content as bytes.

        Example:
            client: { node: create_client }
            file_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        request = client.files.export_media(
            fileId=file_id,
            mimeType=EXPORT_PDF,
        )
        content = await asyncio.to_thread(request.execute)
        if isinstance(content, str):
            return content.encode("latin-1")
        return content

    # ============================================================================
    # Folder Navigation
    # ============================================================================

    @opcode(category="drive")
    async def drive_get_folder_id_by_name(
        client: DriveClient,
        folder_name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Optional[str]:
        """Find a folder's ID by its name.

        Args:
            client: DriveClient from drive_create_client.
            folder_name: Exact name of the folder to find.
            parent_folder_id: Restrict search to a specific parent folder.

        Returns:
            Folder ID string if found, None if not found.

        Example:
            client: { node: create_client }
            folder_name: "Transcrições de Reuniões"
        """
        q_parts = [
            f"name = '{folder_name}'",
            f"mimeType = '{MIME_GOOGLE_FOLDER}'",
            "trashed = false",
        ]
        if parent_folder_id:
            q_parts.append(f"'{parent_folder_id}' in parents")
        q = " and ".join(q_parts)

        request = client.files.list(
            q=q,
            pageSize=1,
            fields="files(id, name)",
        )
        result = await asyncio.to_thread(request.execute)
        files = result.get("files", [])
        return files[0]["id"] if files else None

    @opcode(category="drive")
    async def drive_list_folders(
        client: DriveClient,
        parent_folder_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all folders accessible in Google Drive.

        Args:
            client: DriveClient from drive_create_client.
            parent_folder_id: Parent folder ID to list subfolders of.
                If None, lists all accessible folders.

        Returns:
            List of folder dicts with id, name, and modifiedTime.

        Example:
            client: { node: create_client }
            parent_folder_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        """
        q_parts = [f"mimeType = '{MIME_GOOGLE_FOLDER}'", "trashed = false"]
        if parent_folder_id:
            q_parts.append(f"'{parent_folder_id}' in parents")
        q = " and ".join(q_parts)

        request = client.files.list(
            q=q,
            pageSize=100,
            fields="files(id, name, modifiedTime)",
            orderBy="name",
        )
        result = await asyncio.to_thread(request.execute)
        return result.get("files", [])
