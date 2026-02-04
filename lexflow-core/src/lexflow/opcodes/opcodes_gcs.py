"""Google Cloud Storage opcodes for LexFlow.

This module provides opcodes for interacting with Google Cloud Storage buckets
using native async support via gcloud-aio-storage.

Installation:
    pip install lexflow[gcs]

Authentication:
    GCS uses Application Default Credentials (ADC):
    - gcloud auth application-default login (for local development)
    - GOOGLE_APPLICATION_CREDENTIALS environment variable (for service accounts)
    - Automatic metadata server (for GCE/GKE/Cloud Run)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from gcloud.aio.storage import Storage


class GCSObjectMetadata(TypedDict, total=False):
    """Metadata for a GCS object."""

    name: str
    bucket: str
    size: str
    contentType: str
    updated: str
    md5Hash: str
    generation: str
    metageneration: str
    etag: str
    crc32c: str
    storageClass: str
    timeCreated: str

try:
    from gcloud.aio.storage import Storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


def register_gcs_opcodes():
    """Register GCS opcodes to the default registry."""
    if not GCS_AVAILABLE:
        return

    from .opcodes import opcode, register_category

    register_category(
        id="gcs",
        label="Cloud Storage",
        prefix="gcs_",
        color="#4285F4",
        icon="☁️",
        requires="gcs",
        order=220,
    )

    @opcode(category="gcs")
    async def gcs_create_client(
        service_file: Optional[str] = None,
    ) -> Storage:
        """Create a Google Cloud Storage async client.

        Args:
            service_file: Optional path to service account JSON file

        Returns:
            Storage client instance

        Example:
            service_file: "/path/to/service-account.json"

        Authentication:
            Uses Google Cloud authentication in this order:
            1. service_file parameter (if provided)
            2. GOOGLE_APPLICATION_CREDENTIALS environment variable
            3. gcloud auth application-default login
            4. GCE/GKE metadata server (in cloud environments)
        """
        return Storage(service_file=service_file)

    @opcode(category="gcs")
    async def gcs_list_objects(
        client: Storage,
        bucket_name: str,
        prefix: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> list[GCSObjectMetadata]:
        """List objects in a GCS bucket.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            prefix: Optional prefix to filter objects
            max_results: Optional maximum number of results

        Returns:
            List of object metadata dictionaries

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            prefix: "uploads/"
        """
        params: dict[str, str | int] = {}
        if prefix:
            params["prefix"] = prefix
        if max_results:
            params["maxResults"] = max_results

        result = await client.list_objects(bucket_name, params=params)
        return result.get("items", [])

    @opcode(category="gcs")
    async def gcs_object_exists(
        client: Storage,
        bucket_name: str,
        object_name: str,
    ) -> bool:
        """Check if an object exists in a GCS bucket.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path of the object to check

        Returns:
            True if object exists, False otherwise

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "path/to/file.pdf"
        """
        try:
            await client.download_metadata(bucket_name, object_name)
            return True
        except Exception:
            return False

    @opcode(category="gcs")
    async def gcs_get_object_metadata(
        client: Storage,
        bucket_name: str,
        object_name: str,
    ) -> GCSObjectMetadata:
        """Get metadata for an object in GCS.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path of the object

        Returns:
            Dictionary with object metadata including:
            - name: Object name
            - size: Size in bytes
            - contentType: MIME type
            - updated: Last modification timestamp
            - md5Hash: MD5 hash of content

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "path/to/file.pdf"
        """
        return await client.download_metadata(bucket_name, object_name)

    @opcode(category="gcs")
    async def gcs_download_object_as_bytes(
        client: Storage,
        bucket_name: str,
        object_name: str,
    ) -> bytes:
        """Download an object from GCS as bytes.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path of the object in the bucket

        Returns:
            Object content as bytes

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "path/to/file.pdf"
        """
        return await client.download(bucket_name, object_name)

    @opcode(category="gcs")
    async def gcs_download_object_as_string(
        client: Storage,
        bucket_name: str,
        object_name: str,
        encoding: str = "utf-8",
    ) -> str:
        """Download an object from GCS as a string.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path of the object in the bucket
            encoding: Text encoding (default: utf-8)

        Returns:
            Object content as string

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "path/to/file.txt"
        """
        data = await client.download(bucket_name, object_name)
        return data.decode(encoding)

    @opcode(category="gcs")
    async def gcs_upload_object_from_bytes(
        client: Storage,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> GCSObjectMetadata:
        """Upload bytes to an object in GCS.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path for the object in the bucket
            data: Bytes content to upload
            content_type: Optional MIME type (e.g., "application/pdf")

        Returns:
            Dictionary with upload metadata

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "uploads/document.pdf"
            data: { variable: pdf_bytes }
            content_type: "application/pdf"
        """
        return await client.upload(
            bucket_name,
            object_name,
            data,
            content_type=content_type,
        )

    @opcode(category="gcs")
    async def gcs_upload_object_from_string(
        client: Storage,
        bucket_name: str,
        object_name: str,
        data: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
    ) -> GCSObjectMetadata:
        """Upload a string to an object in GCS.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path for the object in the bucket
            data: String content to upload
            content_type: MIME type (default: "text/plain")
            encoding: Text encoding (default: utf-8)

        Returns:
            Dictionary with upload metadata

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "logs/output.txt"
            data: "Hello, World!"
        """
        return await client.upload(
            bucket_name,
            object_name,
            data.encode(encoding),
            content_type=content_type,
        )

    @opcode(category="gcs")
    async def gcs_delete_object(
        client: Storage,
        bucket_name: str,
        object_name: str,
    ) -> bool:
        """Delete an object from GCS.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket
            object_name: Name/path of the object to delete

        Returns:
            True if deletion was successful

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket"
            object_name: "path/to/file.pdf"
        """
        await client.delete(bucket_name, object_name)
        return True

    @opcode(category="gcs")
    async def gcs_copy_object(
        client: Storage,
        source_bucket: str,
        source_object: str,
        dest_bucket: str,
        dest_object: str,
    ) -> GCSObjectMetadata:
        """Copy an object within or between GCS buckets.

        Args:
            client: GCS client instance (from gcs_create_client)
            source_bucket: Source bucket name
            source_object: Source object name/path
            dest_bucket: Destination bucket name
            dest_object: Destination object name/path

        Returns:
            Dictionary with copy operation metadata

        Example:
            client: { node: my_client }
            source_bucket: "source-bucket"
            source_object: "path/to/file.pdf"
            dest_bucket: "dest-bucket"
            dest_object: "backup/file.pdf"
        """
        return await client.copy(
            source_bucket,
            source_object,
            dest_bucket,
            new_name=dest_object,
        )

    @opcode(category="gcs")
    async def gcs_close_client(client: Storage) -> bool:
        """Close the GCS client and release resources.

        Args:
            client: GCS client instance to close

        Returns:
            True when closed successfully

        Example:
            client: { node: my_client }
        """
        await client.close()
        return True
