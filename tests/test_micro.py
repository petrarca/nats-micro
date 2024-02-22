from __future__ import annotations

import contextlib
from typing import AsyncIterator

import pytest
import pytest_asyncio
from nats.aio.client import Client as NATS
from nats_contrib.test_server import NATSD

from nats_contrib import micro
from nats_contrib.micro.client import MicroClient


@pytest.mark.asyncio
class MicroTestSetup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, nats_server: NATSD, nats_client: NATS) -> AsyncIterator[None]:
        self.nats_server = nats_server
        self.nats_client = nats_client
        self.micro_client = MicroClient(nats_client)
        self.test_stack = contextlib.AsyncExitStack()
        async with self.test_stack:
            yield None


class TestMicro(MicroTestSetup):
    async def test_ping(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ):
            results = await self.micro_client.ping(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            # Save instance id
            instance_id = results[0].id
            results = await self.micro_client.ping(service="service1", max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            results = await self.micro_client.service("service1").ping(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            result = (
                await self.micro_client.service("service1").instance(instance_id).ping()
            )
            assert result.name == "service1"
            assert result.version == "0.0.1"
            assert result.id == instance_id

    async def test_info(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ):
            results = await self.micro_client.info(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == []
            # Save instance id
            instance_id = results[0].id
            results = await self.micro_client.info(service="service1", max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            results = await self.micro_client.service("service1").info(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            result = (
                await self.micro_client.service("service1").instance(instance_id).info()
            )
            assert result.name == "service1"
            assert result.version == "0.0.1"
            assert result.id == instance_id

    async def test_stats(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ):
            results = await self.micro_client.stats(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == []
            # Save instance id
            instance_id = results[0].id
            results = await self.micro_client.stats(service="service1", max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            results = await self.micro_client.service("service1").stats(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].id == instance_id
            result = (
                await self.micro_client.service("service1")
                .instance(instance_id)
                .stats()
            )
            assert result.name == "service1"
            assert result.version == "0.0.1"
            assert result.id == instance_id


class TestMicroEndpoint(MicroTestSetup):
    async def handler(self, request: micro.Request) -> None:
        await request.respond(b"OK")

    async def test_info(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            await service.add_endpoint(
                "endpoint1",
                self.handler,
            )
            results = await self.micro_client.info(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointInfo(
                    name="endpoint1", subject="endpoint1", queue_group="q", metadata={}
                )
            ]

    async def test_stats(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            await service.add_endpoint(
                "endpoint1",
                self.handler,
            )
            results = await self.micro_client.stats(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointStats(
                    name="endpoint1",
                    subject="endpoint1",
                    queue_group="q",
                    num_errors=0,
                    num_requests=0,
                    last_error="",
                    processing_time=0,
                    average_processing_time=0,
                    data={},
                )
            ]


class TestMicroEndpointWithSubject(MicroTestSetup):
    async def handler(self, request: micro.Request) -> None:
        await request.respond(b"OK")

    async def test_info(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            await service.add_endpoint(
                "endpoint1",
                self.handler,
                subject="other",
            )
            results = await self.micro_client.info(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointInfo(
                    name="endpoint1", subject="other", queue_group="q", metadata={}
                )
            ]

    async def test_stats(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            await service.add_endpoint(
                "endpoint1",
                self.handler,
                subject="other",
            )
            results = await self.micro_client.stats(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointStats(
                    name="endpoint1",
                    subject="other",
                    queue_group="q",
                    num_errors=0,
                    num_requests=0,
                    last_error="",
                    processing_time=0,
                    average_processing_time=0,
                    data={},
                )
            ]


class TestMicroGroup(MicroTestSetup):
    async def handler(self, request: micro.Request) -> None:
        await request.respond(b"OK")

    async def test_info(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            group = service.add_group("group1", queue_group="q1")
            await group.add_endpoint(
                "endpoint1",
                self.handler,
            )
            results = await self.micro_client.info(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointInfo(
                    name="endpoint1",
                    subject="group1.endpoint1",
                    queue_group="q1",
                    metadata={},
                )
            ]

    async def test_stats(self) -> None:
        async with micro.add_service(
            self.nats_client,
            "service1",
            "0.0.1",
        ) as service:
            group = service.add_group("group1", queue_group="q1")
            await group.add_endpoint(
                "endpoint1",
                self.handler,
            )
            results = await self.micro_client.stats(max_count=1)
            assert len(results) == 1
            assert results[0].name == "service1"
            assert results[0].version == "0.0.1"
            assert results[0].endpoints == [
                micro.EndpointStats(
                    name="endpoint1",
                    subject="group1.endpoint1",
                    queue_group="q1",
                    num_errors=0,
                    num_requests=0,
                    last_error="",
                    processing_time=0,
                    average_processing_time=0,
                    data={},
                )
            ]