"""Unit tests for LLM service with Ollama."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.llm_service import (
    OllamaService,
    ToolContext,
    execute_tool,
    get_admin_tools,
    get_user_tools,
)


class TestToolDefinitions:
    """Tests for tool definition functions."""

    def test_get_user_tools_returns_read_only_tools(self):
        """Verify user tools are read-only operations."""
        tools = get_user_tools()
        assert len(tools) == 3

        tool_names = [t["function"]["name"] for t in tools]
        assert "get_balance" in tool_names
        assert "list_bills" in tool_names
        assert "get_period_info" in tool_names
        assert "create_service_period" not in tool_names

    def test_get_admin_tools_includes_write_operations(self):
        """Verify admin tools include write operations."""
        tools = get_admin_tools()
        assert len(tools) == 4

        tool_names = [t["function"]["name"] for t in tools]
        assert "get_balance" in tool_names
        assert "list_bills" in tool_names
        assert "get_period_info" in tool_names
        assert "create_service_period" in tool_names

    def test_tool_schemas_are_valid(self):
        """Verify all tool schemas have required structure."""
        for tools_fn in [get_user_tools, get_admin_tools]:
            for tool in tools_fn():
                assert tool["type"] == "function"
                assert "function" in tool
                assert "name" in tool["function"]
                assert "description" in tool["function"]
                assert "parameters" in tool["function"]
                assert tool["function"]["parameters"]["type"] == "object"


class TestToolExecution:
    """Tests for tool execution."""

    @pytest.mark.asyncio
    async def test_execute_unknown_tool_returns_error(self):
        """Test that unknown tools return error."""
        ctx = ToolContext(user_id=1, is_admin=False, session=MagicMock())
        result = await execute_tool("unknown_tool", {}, ctx)
        data = json.loads(result)
        assert "error" in data
        assert "Unknown tool" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_get_balance_user_not_found(self):
        """Test get_balance when user not found."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=999, is_admin=False, session=mock_session)

        with patch("src.services.llm_service.BalanceCalculationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_user_by_id = AsyncMock(return_value=None)
            mock_service_cls.return_value = mock_service

            result = await execute_tool("get_balance", {}, ctx)
            data = json.loads(result)
            assert "error" in data
            assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_get_balance_success(self):
        """Test get_balance returns balance data."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        with patch("src.services.llm_service.BalanceCalculationService") as mock_service_cls:
            mock_user = MagicMock()
            mock_user.name = "Test User"
            mock_account = MagicMock()
            mock_account.updated_at = None

            mock_service = MagicMock()
            mock_service.get_user_by_id = AsyncMock(return_value=mock_user)
            mock_service.get_account_for_user = AsyncMock(return_value=mock_account)
            mock_service.calculate_user_balance = AsyncMock(return_value=100.50)
            mock_service_cls.return_value = mock_service

            result = await execute_tool("get_balance", {}, ctx)
            data = json.loads(result)

            assert data["user_id"] == 1
            assert data["user_name"] == "Test User"
            assert data["balance"] == 100.50
            assert data["currency"] == "USD"

    @pytest.mark.asyncio
    async def test_execute_list_bills_success(self):
        """Test list_bills returns bills data."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        with patch("src.services.llm_service.BalanceCalculationService") as mock_service_cls:
            mock_account = MagicMock()
            mock_bill = MagicMock()
            mock_bill.bill_id = "B001"
            mock_bill.amount = 50.00
            mock_bill.bill_date = "2025-01-15"
            mock_bill.bill_type = "electricity"

            mock_service = MagicMock()
            mock_service.get_account_for_user = AsyncMock(return_value=mock_account)
            mock_service.list_bills_for_user = AsyncMock(return_value=[mock_bill])
            mock_service_cls.return_value = mock_service

            result = await execute_tool("list_bills", {"limit": 5}, ctx)
            data = json.loads(result)

            assert data["user_id"] == 1
            assert len(data["bills"]) == 1
            assert data["bills"][0]["bill_id"] == "B001"

    @pytest.mark.asyncio
    async def test_execute_get_period_info_not_found(self):
        """Test get_period_info when period not found."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        with patch("src.services.llm_service.AsyncServicePeriodService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_period_info = AsyncMock(return_value=None)
            mock_service_cls.return_value = mock_service

            result = await execute_tool("get_period_info", {"period_id": 999}, ctx)
            data = json.loads(result)
            assert "error" in data
            assert "not found" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_get_period_info_success(self):
        """Test get_period_info returns period data."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        with patch("src.services.llm_service.AsyncServicePeriodService") as mock_service_cls:
            mock_period = MagicMock()
            mock_period.period_id = 1
            mock_period.name = "Q1 2025"
            mock_period.start_date = "2025-01-01"
            mock_period.end_date = "2025-03-31"
            mock_period.is_active = True

            mock_service = MagicMock()
            mock_service.get_period_info = AsyncMock(return_value=mock_period)
            mock_service_cls.return_value = mock_service

            result = await execute_tool("get_period_info", {"period_id": 1}, ctx)
            data = json.loads(result)

            assert data["period_id"] == 1
            assert data["name"] == "Q1 2025"
            assert data["active"] is True

    @pytest.mark.asyncio
    async def test_execute_get_period_info_missing_id(self):
        """Test get_period_info without period_id returns error."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        result = await execute_tool("get_period_info", {}, ctx)
        data = json.loads(result)
        assert "error" in data
        assert "period_id is required" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_create_period_non_admin_blocked(self):
        """Test create_service_period blocked for non-admin."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=False, session=mock_session)

        result = await execute_tool(
            "create_service_period",
            {"name": "Test", "start_date": "2025-01-01", "end_date": "2025-03-31"},
            ctx,
        )
        data = json.loads(result)
        assert "error" in data
        assert "Admin access required" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_create_period_invalid_date(self):
        """Test create_service_period with invalid date format."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=True, session=mock_session)

        result = await execute_tool(
            "create_service_period",
            {"name": "Test", "start_date": "invalid", "end_date": "2025-03-31"},
            ctx,
        )
        data = json.loads(result)
        assert "error" in data
        assert "Invalid date format" in data["error"]

    @pytest.mark.asyncio
    async def test_execute_create_period_success(self):
        """Test create_service_period succeeds for admin."""
        mock_session = AsyncMock()
        ctx = ToolContext(user_id=1, is_admin=True, session=mock_session)

        with patch("src.services.llm_service.AsyncServicePeriodService") as mock_service_cls:
            from datetime import date

            mock_period = MagicMock()
            mock_period.id = 5
            mock_period.name = "Q1 2025"
            mock_period.start_date = date(2025, 1, 1)
            mock_period.end_date = date(2025, 3, 31)

            mock_service = MagicMock()
            mock_service.create_period = AsyncMock(return_value=mock_period)
            mock_service_cls.return_value = mock_service

            result = await execute_tool(
                "create_service_period",
                {"name": "Q1 2025", "start_date": "2025-01-01", "end_date": "2025-03-31"},
                ctx,
            )
            data = json.loads(result)

            assert data["success"] is True
            assert data["period_id"] == 5
            assert data["name"] == "Q1 2025"


class TestOllamaService:
    """Tests for OllamaService class."""

    def test_init_with_defaults(self):
        """Test OllamaService initialization with defaults."""
        mock_session = MagicMock()

        with patch.dict("os.environ", {"OLLAMA_MODEL": "test-model"}):
            service = OllamaService(session=mock_session, user_id=1)

        assert service.user_id == 1
        assert service.is_admin is False
        assert service.model == "test-model"

    def test_init_with_admin(self):
        """Test OllamaService initialization for admin user."""
        mock_session = MagicMock()
        service = OllamaService(
            session=mock_session,
            user_id=1,
            is_admin=True,
            model="custom-model",
        )

        assert service.is_admin is True
        assert service.model == "custom-model"

    def test_get_tools_for_user(self):
        """Test user gets read-only tools."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1, is_admin=False)

        tools = service._get_tools()
        tool_names = [t["function"]["name"] for t in tools]
        assert "create_service_period" not in tool_names

    def test_get_tools_for_admin(self):
        """Test admin gets all tools including write operations."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1, is_admin=True)

        tools = service._get_tools()
        tool_names = [t["function"]["name"] for t in tools]
        assert "create_service_period" in tool_names

    @pytest.mark.asyncio
    async def test_chat_returns_response(self):
        """Test chat returns LLM response."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1)

        mock_message = MagicMock()
        mock_message.content = "Your balance is $100.50"
        mock_message.tool_calls = None

        mock_response = MagicMock()
        mock_response.message = mock_message

        with patch.object(service.client, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response

            result = await service.chat("What is my balance?")

            assert result == "Your balance is $100.50"
            mock_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_handles_tool_call(self):
        """Test chat handles tool calls and returns final response."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1)

        # First response with tool call
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "get_balance"
        mock_tool_call.function.arguments = {}
        mock_tool_call.id = "call_1"

        mock_message_1 = MagicMock()
        mock_message_1.content = ""
        mock_message_1.tool_calls = [mock_tool_call]

        mock_response_1 = MagicMock()
        mock_response_1.message = mock_message_1

        # Second response with final answer
        mock_message_2 = MagicMock()
        mock_message_2.content = "Your balance is $100.50"
        mock_message_2.tool_calls = None

        mock_response_2 = MagicMock()
        mock_response_2.message = mock_message_2

        with patch.object(service.client, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = [mock_response_1, mock_response_2]

            with patch(
                "src.services.llm_service.execute_tool", new_callable=AsyncMock
            ) as mock_execute:
                mock_execute.return_value = json.dumps({"balance": 100.50})

                result = await service.chat("What is my balance?")

                assert result == "Your balance is $100.50"
                assert mock_chat.call_count == 2
                mock_execute.assert_called_once_with("get_balance", {}, service.tool_context)

    @pytest.mark.asyncio
    async def test_chat_handles_connection_error(self):
        """Test chat handles Ollama connection errors gracefully."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1)

        with patch.object(service.client, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = ConnectionError("Connection refused")

            result = await service.chat("Hello")

            assert "error" in result.lower()
            assert "Connection refused" in result

    @pytest.mark.asyncio
    async def test_chat_max_tool_calls_limit(self):
        """Test chat respects max tool calls limit."""
        mock_session = MagicMock()
        service = OllamaService(session=mock_session, user_id=1)

        # Always return tool call (infinite loop scenario)
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "get_balance"
        mock_tool_call.function.arguments = {}

        mock_message = MagicMock()
        mock_message.content = ""
        mock_message.tool_calls = [mock_tool_call]

        mock_response = MagicMock()
        mock_response.message = mock_message

        with patch.object(service.client, "chat", new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response

            with patch(
                "src.services.llm_service.execute_tool", new_callable=AsyncMock
            ) as mock_execute:
                mock_execute.return_value = json.dumps({"balance": 100})

                result = await service.chat("Hello", max_tool_calls=3)

                assert "limit" in result.lower() or "simpler" in result.lower()
                # Should have called tool 3 times (max_tool_calls)
                assert mock_execute.call_count == 3
