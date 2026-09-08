import asyncio

from mcp import Client

from app.mcp.server import mcp


def test_mcp_server_exposes_evidence_tool() -> None:
    async def exercise() -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert [tool.name for tool in tools.tools] == ["get_incident_evidence"]

            result = await client.call_tool(
                "get_incident_evidence",
                {"scenario_id": "database-pool-exhaustion", "operation": "get", "evidence_id": "ev-db-001"},
            )
            assert result.structured_content is not None
            assert result.structured_content["result"][0]["id"] == "ev-db-001"

    asyncio.run(exercise())
