"""Google Cloud Pub/Sub opcodes for LexFlow.

This module provides opcodes for publishing and consuming messages
from Google Cloud Pub/Sub using native async via gcloud-aio-pubsub.

Installation:
    pip install lexflow[pubsub]

Authentication:
    Pub/Sub uses Application Default Credentials (ADC):
    - gcloud auth application-default login (for local development)
    - GOOGLE_APPLICATION_CREDENTIALS environment variable (for service accounts)
    - Automatic metadata server (for GCE/GKE/Cloud Run)
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional, AsyncGenerator

# Reserved keys that cannot be used as message attributes (conflict with publish params)
_RESERVED_ATTRIBUTE_KEYS = {"topic", "data", "ordering_key"}


if TYPE_CHECKING:
    from gcloud.aio.pubsub import PublisherClient, SubscriberClient

try:
    from aiohttp import ClientError
    from gcloud.aio.pubsub import PublisherClient, SubscriberClient, PubsubMessage

    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False
    ClientError = Exception  # Fallback for type checking


def register_pubsub_opcodes():
    """Register Pub/Sub opcodes to the default registry."""
    if not PUBSUB_AVAILABLE:
        return

    from .opcodes import opcode, register_category

    register_category(
        id="pubsub",
        label="Pub/Sub",
        prefix="pubsub_",
        color="#EA4335",
        icon="📨",
        requires="pubsub",
        order=270,
    )

    @opcode(category="pubsub")
    async def pubsub_create_publisher() -> PublisherClient:
        """Create a Google Cloud Pub/Sub publisher client.

        Returns:
            PublisherClient instance

        Example:
            (no inputs required)

        Authentication:
            Requires Google Cloud authentication via:
            - gcloud auth application-default login
            - Or GOOGLE_APPLICATION_CREDENTIALS environment variable

        Note:
            Supports PUBSUB_EMULATOR_HOST environment variable for local testing.
            When set, authentication is automatically skipped.
        """
        # gcloud-aio-pubsub automatically detects PUBSUB_EMULATOR_HOST
        # and skips authentication when in emulator mode
        return PublisherClient()

    @opcode(category="pubsub")
    async def pubsub_create_subscriber() -> SubscriberClient:
        """Create a Google Cloud Pub/Sub subscriber client.

        Returns:
            SubscriberClient instance

        Example:
            (no inputs required)

        Authentication:
            Requires Google Cloud authentication via:
            - gcloud auth application-default login
            - Or GOOGLE_APPLICATION_CREDENTIALS environment variable

        Note:
            Supports PUBSUB_EMULATOR_HOST environment variable for local testing.
            When set, authentication is automatically skipped.
        """
        # gcloud-aio-pubsub automatically detects PUBSUB_EMULATOR_HOST
        # and skips authentication when in emulator mode
        return SubscriberClient()

    @opcode(category="pubsub")
    async def pubsub_publish_message(
        publisher: PublisherClient,
        project_id: str,
        topic_id: str,
        data: str,
    ) -> str:
        """Publish a message to a Pub/Sub topic.

        Args:
            publisher: Publisher client instance (from pubsub_create_publisher)
            project_id: GCP project ID
            topic_id: Topic ID (not the full path)
            data: Message data as string

        Returns:
            Message ID of the published message

        Example:
            publisher: { variable: my_publisher }
            project_id: "my-gcp-project"
            topic_id: "my-topic"
            data: "Hello, Pub/Sub!"
        """
        topic_path = f"projects/{project_id}/topics/{topic_id}"
        message = PubsubMessage(data.encode("utf-8"))
        response = await publisher.publish(topic_path, [message])
        return response["messageIds"][0]

    @opcode(category="pubsub")
    async def pubsub_publish_message_with_attributes(
        publisher: PublisherClient,
        project_id: str,
        topic_id: str,
        data: str,
        attributes: dict,
    ) -> str:
        """Publish a message with custom attributes to a Pub/Sub topic.

        Args:
            publisher: Publisher client instance (from pubsub_create_publisher)
            project_id: GCP project ID
            topic_id: Topic ID (not the full path)
            data: Message data as string
            attributes: Dictionary of custom attributes (string keys and values)

        Returns:
            Message ID of the published message

        Example:
            publisher: { variable: my_publisher }
            project_id: "my-gcp-project"
            topic_id: "my-topic"
            data: "Hello with attributes!"
            attributes: { "type": "greeting", "priority": "high" }
        """
        topic_path = f"projects/{project_id}/topics/{topic_id}"

        # Ensure all attribute values are strings and filter reserved keys
        str_attributes = {
            str(k): str(v)
            for k, v in attributes.items()
            if str(k) not in _RESERVED_ATTRIBUTE_KEYS
        }

        message = PubsubMessage(data.encode("utf-8"), **str_attributes)
        response = await publisher.publish(topic_path, [message])
        return response["messageIds"][0]

    @opcode(category="pubsub")
    async def pubsub_pull_messages(
        subscriber: SubscriberClient,
        project_id: str,
        subscription_id: str,
        max_messages: int = 10,
    ) -> list:
        """Pull messages from a Pub/Sub subscription.

        Args:
            subscriber: Subscriber client instance (from pubsub_create_subscriber)
            project_id: GCP project ID
            subscription_id: Subscription ID (not the full path)
            max_messages: Maximum number of messages to pull (default: 10)

        Returns:
            List of message dictionaries with keys:
            - ack_id: Acknowledgment ID (needed for acknowledging)
            - message_id: Message ID
            - data: Message data as string
            - attributes: Message attributes dictionary
            - publish_time: Publish timestamp as ISO string

        Example:
            subscriber: { variable: my_subscriber }
            project_id: "my-gcp-project"
            subscription_id: "my-subscription"
            max_messages: 5
        """
        subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"
        # pull() returns list[SubscriberMessage] objects
        subscriber_messages = await subscriber.pull(
            subscription_path, max_messages=max_messages
        )

        messages = []
        for msg in subscriber_messages:
            # Decode bytes data to string
            data = ""
            if msg.data:
                try:
                    data = msg.data.decode("utf-8")
                except UnicodeDecodeError:
                    data = msg.data.decode("utf-8", errors="replace")

            messages.append(
                {
                    "ack_id": msg.ack_id,
                    "message_id": msg.message_id,
                    "data": data,
                    "attributes": msg.attributes or {},
                    "publish_time": (
                        msg.publish_time.isoformat() if msg.publish_time else None
                    ),
                }
            )

        return messages

    @opcode(category="pubsub")
    async def pubsub_acknowledge_messages(
        subscriber: SubscriberClient,
        project_id: str,
        subscription_id: str,
        ack_ids: list,
    ) -> bool:
        """Acknowledge messages that have been processed.

        Args:
            subscriber: Subscriber client instance (from pubsub_create_subscriber)
            project_id: GCP project ID
            subscription_id: Subscription ID (not the full path)
            ack_ids: List of acknowledgment IDs from pulled messages

        Returns:
            True if acknowledgment was successful

        Example:
            subscriber: { variable: my_subscriber }
            project_id: "my-gcp-project"
            subscription_id: "my-subscription"
            ack_ids: { variable: message_ack_ids }
        """
        subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"
        await subscriber.acknowledge(subscription_path, ack_ids)
        return True

    @opcode(category="pubsub")
    async def pubsub_publish_batch(
        publisher: PublisherClient,
        project_id: str,
        topic_id: str,
        messages: list,
    ) -> list:
        """Publish multiple messages to a Pub/Sub topic.

        Args:
            publisher: Publisher client instance (from pubsub_create_publisher)
            project_id: GCP project ID
            topic_id: Topic ID (not the full path)
            messages: List of message dictionaries, each with:
                - data: Message data as string (required)
                - attributes: Optional dictionary of attributes

        Returns:
            List of message IDs for the published messages

        Example:
            publisher: { variable: my_publisher }
            project_id: "my-gcp-project"
            topic_id: "my-topic"
            messages:
              - data: "First message"
                attributes: { "index": "1" }
              - data: "Second message"
                attributes: { "index": "2" }
        """
        topic_path = f"projects/{project_id}/topics/{topic_id}"

        if not messages:
            return []

        pubsub_messages = []
        for i, msg in enumerate(messages):
            data = msg.get("data")
            if data is None or data == "":
                raise ValueError(f"Message at index {i} has empty or missing data")
            data_bytes = data.encode("utf-8") if isinstance(data, str) else data
            attributes = msg.get("attributes", {})

            # Filter reserved keys to prevent parameter injection
            str_attributes = {
                str(k): str(v)
                for k, v in attributes.items()
                if str(k) not in _RESERVED_ATTRIBUTE_KEYS
            }

            pubsub_messages.append(PubsubMessage(data_bytes, **str_attributes))

        response = await publisher.publish(topic_path, pubsub_messages)
        return response.get("messageIds", [])

    @opcode(category="pubsub")
    async def pubsub_subscribe_stream(
        subscriber: SubscriberClient,
        project_id: str,
        subscription_id: str,
        timeout: Optional[float] = None,
        max_messages: Optional[int] = None,
        batch_size: int = 10,
        min_poll_interval: float = 0.1,
        max_poll_interval: float = 5.0,
        max_retries: int = 10,
    ) -> AsyncGenerator[dict, None]:
        """Subscribe to a Pub/Sub subscription and stream messages as an async generator.

        This opcode returns an async generator that yields messages as they arrive.
        Use with control_async_foreach to process messages continuously.

        Uses exponential backoff when no messages are available: starts at
        min_poll_interval and doubles up to max_poll_interval. Resets to
        min_poll_interval when messages are received.

        Args:
            subscriber: Subscriber client instance (from pubsub_create_subscriber)
            project_id: GCP project ID
            subscription_id: Subscription ID (not the full path)
            timeout: Optional timeout in seconds. If None, runs indefinitely.
            max_messages: Optional max number of messages to receive before stopping.
            batch_size: Messages to pull per request (default: 10)
            min_poll_interval: Initial/minimum sleep between polls in seconds (default: 0.1)
            max_poll_interval: Maximum sleep during backoff in seconds (default: 5.0)
            max_retries: Maximum consecutive errors before raising (default: 10)

        Yields:
            Message dictionaries with keys:
            - ack_id: Acknowledgment ID
            - message_id: Message ID
            - data: Message data as string
            - attributes: Message attributes dictionary
            - publish_time: Publish timestamp as ISO string

        Note:
            The subscriber client is NOT closed by this opcode. Use
            pubsub_close_subscriber to clean up after streaming completes.

        Example:
            subscriber: { variable: my_subscriber }
            project_id: "my-gcp-project"
            subscription_id: "my-subscription"
            timeout: 60
            max_messages: 100
            batch_size: 20
            min_poll_interval: 0.05
            max_poll_interval: 10.0

        Usage in workflow:
            create_subscriber:
              opcode: pubsub_create_subscriber
              isReporter: true

            subscribe:
              opcode: pubsub_subscribe_stream
              isReporter: true
              inputs:
                subscriber: { node: create_subscriber }
                project_id: { variable: project_id }
                subscription_id: { variable: subscription_id }
                timeout: { literal: 30 }
                batch_size: { literal: 20 }

            process_messages:
              opcode: control_async_foreach
              inputs:
                VAR: { literal: "msg" }
                ITERABLE: { node: subscribe }
              branches:
                BODY:
                  - handle_message
        """
        subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"

        async def message_generator():
            message_count = 0
            error_count = 0
            poll_interval = min_poll_interval
            loop = asyncio.get_running_loop()
            start_time = loop.time()

            while True:
                # Check timeout
                if timeout:
                    elapsed = loop.time() - start_time
                    if elapsed >= timeout:
                        break

                # Check max_messages
                if max_messages and message_count >= max_messages:
                    break

                # Calculate effective batch size
                effective_batch_size = batch_size
                if max_messages:
                    effective_batch_size = min(batch_size, max_messages - message_count)

                try:
                    # pull() returns list[SubscriberMessage] objects
                    subscriber_messages = await subscriber.pull(
                        subscription_path, max_messages=effective_batch_size
                    )
                    error_count = 0  # Reset on success
                except (ClientError, asyncio.TimeoutError):
                    # Normal when no messages available (especially with emulator)
                    await asyncio.sleep(poll_interval)
                    poll_interval = min(poll_interval * 2, max_poll_interval)
                    continue
                except Exception as e:
                    error_count += 1
                    if error_count >= max_retries:
                        logging.error(
                            f"Max retries ({max_retries}) exceeded pulling messages: {e}"
                        )
                        raise
                    logging.warning(
                        f"Error pulling messages (attempt {error_count}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(poll_interval)
                    poll_interval = min(poll_interval * 2, max_poll_interval)
                    continue

                if not subscriber_messages:
                    # No messages, apply exponential backoff
                    await asyncio.sleep(poll_interval)
                    poll_interval = min(poll_interval * 2, max_poll_interval)
                    continue

                # Messages received, reset to minimum poll interval
                poll_interval = min_poll_interval

                for msg in subscriber_messages:
                    # Decode bytes data to string
                    data = ""
                    if msg.data:
                        try:
                            data = msg.data.decode("utf-8")
                        except UnicodeDecodeError:
                            data = msg.data.decode("utf-8", errors="replace")

                    yield {
                        "ack_id": msg.ack_id,
                        "message_id": msg.message_id,
                        "data": data,
                        "attributes": msg.attributes or {},
                        "publish_time": (
                            msg.publish_time.isoformat() if msg.publish_time else None
                        ),
                    }

                    message_count += 1

                    # Check limits after each message
                    if max_messages and message_count >= max_messages:
                        return
                    if timeout:
                        elapsed = loop.time() - start_time
                        if elapsed >= timeout:
                            return

        return message_generator()

    @opcode(category="pubsub")
    async def pubsub_ack_message(
        subscriber: SubscriberClient,
        project_id: str,
        subscription_id: str,
        message: dict,
    ) -> bool:
        """Acknowledge a single message received from pubsub_pull_messages.

        Args:
            subscriber: Subscriber client instance
            project_id: GCP project ID
            subscription_id: Subscription ID
            message: Message dictionary with ack_id from pubsub_pull_messages

        Returns:
            True if acknowledged successfully

        Example:
            subscriber: { variable: my_subscriber }
            project_id: "my-gcp-project"
            subscription_id: "my-subscription"
            message: { variable: msg }
        """
        if "ack_id" not in message:
            raise ValueError("Invalid message: missing ack_id")

        subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"
        await subscriber.acknowledge(subscription_path, [message["ack_id"]])
        return True

    @opcode(category="pubsub")
    async def pubsub_nack_message(
        subscriber: SubscriberClient,
        project_id: str,
        subscription_id: str,
        message: dict,
    ) -> bool:
        """Negative-acknowledge a message (return to queue for redelivery).

        Args:
            subscriber: Subscriber client instance
            project_id: GCP project ID
            subscription_id: Subscription ID
            message: Message dictionary with ack_id from pubsub_pull_messages

        Returns:
            True if nack'd successfully

        Example:
            subscriber: { variable: my_subscriber }
            project_id: "my-gcp-project"
            subscription_id: "my-subscription"
            message: { variable: msg }
        """
        if "ack_id" not in message:
            raise ValueError("Invalid message: missing ack_id")

        subscription_path = f"projects/{project_id}/subscriptions/{subscription_id}"
        await subscriber.modify_ack_deadline(subscription_path, [message["ack_id"]], 0)
        return True

    @opcode(category="pubsub")
    async def pubsub_close_publisher(publisher: PublisherClient) -> bool:
        """Close the publisher client and release resources.

        Args:
            publisher: Publisher client instance to close

        Returns:
            True if closed successfully

        Example:
            publisher: { variable: my_publisher }
        """
        await publisher.close()
        return True

    @opcode(category="pubsub")
    async def pubsub_close_subscriber(subscriber: SubscriberClient) -> bool:
        """Close the subscriber client and release resources.

        Args:
            subscriber: Subscriber client instance to close

        Returns:
            True if closed successfully

        Example:
            subscriber: { variable: my_subscriber }
        """
        await subscriber.close()
        return True
