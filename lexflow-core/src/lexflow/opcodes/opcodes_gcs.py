"""Google Cloud Storage opcodes for LexFlow.

This module provides opcodes for interacting with Google Cloud Storage buckets.

Installation:
    pip install lexflow[gcs]

Authentication:
    GCS uses Application Default Credentials (ADC):
    - gcloud auth application-default login (for local development)
    - GOOGLE_APPLICATION_CREDENTIALS environment variable (for service accounts)
    - Automatic metadata server (for GCE/GKE/Cloud Run)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from google.cloud.storage import Bucket, Client

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


def _check_availability():
    """Check if google-cloud-storage is available and raise helpful error if not."""
    if not GCS_AVAILABLE:
        raise ImportError(
            "google-cloud-storage is not installed. Install it with:\n"
            "  pip install lexflow[gcs]\n"
            "or:\n"
            "  pip install google-cloud-storage"
        )


def register_gcs_opcodes():
    """Register GCS opcodes to the default registry."""
    if not GCS_AVAILABLE:
        return

    from .opcodes import default_registry, register_category

    register_category(
        id="gcs",
        label="Cloud Storage",
        prefix="gcs_",
        color="#4285F4",
        icon="☁️",
        requires="gcs",
        order=220,
    )

    @default_registry.register()
    async def gcs_create_client(project: Optional[str] = None) -> Client:
        """Create a Google Cloud Storage client.

        Args:
            project: Optional GCP project ID (uses default if not specified)

        Returns:
            storage.Client instance

        Example:
            project: "my-gcp-project"

        Authentication:
            Requires Google Cloud authentication via:
            - gcloud auth application-default login
            - Or GOOGLE_APPLICATION_CREDENTIALS environment variable
        """
        _check_availability()

        if project:
            return storage.Client(project=project)
        return storage.Client()

    @default_registry.register()
    async def gcs_get_bucket(client: Client, bucket_name: str) -> Bucket:
        """Get a reference to a GCS bucket.

        Args:
            client: GCS client instance (from gcs_create_client)
            bucket_name: Name of the bucket

        Returns:
            storage.Bucket instance

        Example:
            client: { node: my_client }
            bucket_name: "my-bucket-name"
        """
        _check_availability()

        return client.bucket(bucket_name)

    @default_registry.register()
    async def gcs_object_exists(bucket: Bucket, object_name: str) -> bool:
        """Check if an object exists in a GCS bucket.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path of the object to check

        Returns:
            True if object exists, False otherwise

        Example:
            bucket: { node: my_bucket }
            object_name: "path/to/file.pdf"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        return blob.exists()

    @default_registry.register()
    async def gcs_get_object_metadata(bucket: Bucket, object_name: str) -> dict:
        """Get metadata for an object in GCS.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path of the object

        Returns:
            Dictionary with object metadata including:
            - name: Object name
            - size: Size in bytes
            - content_type: MIME type
            - updated: Last modification timestamp
            - md5_hash: MD5 hash of content

        Example:
            bucket: { node: my_bucket }
            object_name: "path/to/file.pdf"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        blob.reload()

        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "updated": blob.updated.isoformat() if blob.updated else None,
            "md5_hash": blob.md5_hash,
            "generation": blob.generation,
            "metageneration": blob.metageneration,
        }

    @default_registry.register()
    async def gcs_download_object_as_bytes(bucket: Bucket, object_name: str) -> bytes:
        """Download an object from GCS as bytes.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path of the object in the bucket

        Returns:
            Object content as bytes

        Example:
            bucket: { node: my_bucket }
            object_name: "path/to/file.pdf"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        return blob.download_as_bytes()

    @default_registry.register()
    async def gcs_upload_object_from_bytes(
        bucket: Bucket,
        object_name: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> dict:
        """Upload bytes to an object in GCS.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path for the object in the bucket
            data: Bytes content to upload
            content_type: Optional MIME type (e.g., "application/pdf")

        Returns:
            Dictionary with upload metadata including name, size, content_type

        Example:
            bucket: { node: my_bucket }
            object_name: "uploads/document.pdf"
            data: { variable: pdf_bytes }
            content_type: "application/pdf"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        blob.upload_from_string(data, content_type=content_type)

        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
        }

    @default_registry.register()
    async def gcs_upload_object_from_string(
        bucket: Bucket,
        object_name: str,
        data: str,
        content_type: Optional[str] = "text/plain",
    ) -> dict:
        """Upload a string to an object in GCS.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path for the object in the bucket
            data: String content to upload
            content_type: Optional MIME type (defaults to "text/plain")

        Returns:
            Dictionary with upload metadata including name, size, content_type

        Example:
            bucket: { node: my_bucket }
            object_name: "logs/output.txt"
            data: "Hello, World!"
            content_type: "text/plain"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        blob.upload_from_string(data, content_type=content_type)

        return {
            "name": blob.name,
            "size": blob.size,
            "content_type": blob.content_type,
        }

    @default_registry.register()
    async def gcs_delete_object(bucket: Bucket, object_name: str) -> bool:
        """Delete an object from GCS.

        Args:
            bucket: GCS bucket instance (from gcs_get_bucket)
            object_name: Name/path of the object to delete

        Returns:
            True if deletion was successful

        Example:
            bucket: { node: my_bucket }
            object_name: "path/to/file.pdf"
        """
        _check_availability()

        blob = bucket.blob(object_name)
        blob.delete()
        return True
