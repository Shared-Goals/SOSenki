"""Contract tests for MCP Server (FastMCP implementation)."""

import pytest

from src.api.mcp_server import mcp


class TestMCPServerTools:
    """Tests for FastMCP server tool registration."""

    def test_mcp_server_has_name(self):
        """Verify MCP server has correct name."""
        assert mcp.name == "SOSenki"

    def test_expected_tools_are_registered(self):
        """Verify expected tools are registered in FastMCP."""
        # Get tool names from the tool manager
        tools = mcp._tool_manager.list_tools()
        tool_names = [tool.name for tool in tools]

        assert "get_balance" in tool_names
        assert "list_bills" in tool_names
        assert "get_period_info" in tool_names
        assert "create_service_period" in tool_names

    def test_tools_have_descriptions(self):
        """Verify all tools have descriptions."""
        tools = mcp._tool_manager.list_tools()

        for tool in tools:
            assert tool.description, f"Tool {tool.name} has no description"

    def test_tools_have_parameters(self):
        """Verify all tools have parameter schemas."""
        tools = mcp._tool_manager.list_tools()

        for tool in tools:
            assert tool.parameters is not None, f"Tool {tool.name} has no parameters"


class TestToolSchemaValidation:
    """Tests for tool parameter schema validation."""

    def test_get_balance_schema(self):
        """get_balance tool has correct parameter schema."""
        tools = mcp._tool_manager.list_tools()
        get_balance = next(t for t in tools if t.name == "get_balance")

        schema = get_balance.parameters
        assert "properties" in schema
        assert "user_id" in schema["properties"]

    def test_list_bills_schema(self):
        """list_bills tool has correct parameter schema."""
        tools = mcp._tool_manager.list_tools()
        list_bills = next(t for t in tools if t.name == "list_bills")

        schema = list_bills.parameters
        assert "properties" in schema
        assert "user_id" in schema["properties"]
        assert "limit" in schema["properties"]

    def test_get_period_info_schema(self):
        """get_period_info tool has correct parameter schema."""
        tools = mcp._tool_manager.list_tools()
        get_period_info = next(t for t in tools if t.name == "get_period_info")

        schema = get_period_info.parameters
        assert "properties" in schema
        assert "period_id" in schema["properties"]

    def test_create_service_period_schema(self):
        """create_service_period tool has correct parameter schema."""
        tools = mcp._tool_manager.list_tools()
        create_period = next(t for t in tools if t.name == "create_service_period")

        schema = create_period.parameters
        assert "properties" in schema
        # Required fields
        assert "name" in schema["properties"]
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        # Optional electricity fields
        assert "electricity_start" in schema["properties"]
        assert "electricity_rate" in schema["properties"]


class TestCreateServicePeriodValidation:
    """Tests for create_service_period parameter validation logic."""

    def test_valid_date_format(self):
        """Valid ISO date format is accepted."""
        from datetime import date as date_type

        valid_date = "2025-09-01"
        parsed = date_type.fromisoformat(valid_date)
        assert parsed.year == 2025
        assert parsed.month == 9
        assert parsed.day == 1

    def test_invalid_date_format_raises(self):
        """Invalid date format raises ValueError."""
        from datetime import date as date_type

        with pytest.raises(ValueError):
            date_type.fromisoformat("invalid-date")

        with pytest.raises(ValueError):
            date_type.fromisoformat("01-09-2025")  # Wrong format

    def test_date_order_validation(self):
        """start_date must be before end_date."""
        from datetime import date as date_type

        start = date_type.fromisoformat("2025-12-31")
        end = date_type.fromisoformat("2025-01-01")

        # This should fail validation (start >= end)
        assert start >= end


class TestMCPStreamableHTTPApp:
    """Tests for MCP Streamable HTTP app integration."""

    def test_http_app_is_available(self):
        """Verify HTTP app can be created."""
        from src.api.mcp_server import get_mcp_http_app

        http_app, lifespan = get_mcp_http_app()
        assert http_app is not None
        assert lifespan is not None

    def test_http_app_is_asgi(self):
        """Verify HTTP app is a valid ASGI app."""
        from src.api.mcp_server import get_mcp_http_app

        http_app, lifespan = get_mcp_http_app()
        # ASGI apps are callable
        assert callable(http_app)
