"""Unit tests for MCP Server to increase coverage."""

import json
from datetime import date as date_type
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.mcp_server import mcp, mcp_lifespan


class TestDatabaseEngineSetup:
    """Tests for database engine initialization."""

    @pytest.mark.asyncio
    async def test_mcp_lifespan_available(self):
        """Test mcp_lifespan context manager is available."""
        assert mcp_lifespan is not None


class TestMCPLifespanContextManager:
    """Tests for mcp_lifespan context manager."""

    def test_mcp_instance_exists(self):
        """Test MCP instance exists and is properly configured."""
        assert mcp is not None
        assert mcp.name == "SOSenki"


class TestGetBalanceTool:
    """Tests for get_balance MCP tool."""

    @pytest.mark.asyncio
    async def test_get_balance_not_initialized(self):
        """Test get_balance returns error when DB not initialized."""
        # Get the actual function from the tool
        tools = list(mcp._tool_manager._tools.values())
        get_balance_tool = next(t for t in tools if t.name == "get_balance")
        get_balance_fn = get_balance_tool.fn

        import src.api.mcp_server as mcp_module

        old_session_maker = mcp_module._session_maker
        mcp_module._session_maker = None

        result = await get_balance_fn(1)
        result_dict = json.loads(result)

        assert "error" in result_dict
        assert "not initialized" in result_dict["error"].lower()

        mcp_module._session_maker = old_session_maker

    @pytest.mark.asyncio
    async def test_get_balance_user_not_found(self):
        """Test get_balance handles missing user."""
        tools = list(mcp._tool_manager._tools.values())
        get_balance_tool = next(t for t in tools if t.name == "get_balance")
        get_balance_fn = get_balance_tool.fn

        mock_service = AsyncMock()
        mock_service.get_user_by_id = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await get_balance_fn(999)
                result_dict = json.loads(result)

                assert "error" in result_dict
                assert "not found" in result_dict["error"].lower()

    @pytest.mark.asyncio
    async def test_get_balance_no_account(self):
        """Test get_balance handles user without account."""
        tools = list(mcp._tool_manager._tools.values())
        get_balance_tool = next(t for t in tools if t.name == "get_balance")
        get_balance_fn = get_balance_tool.fn

        mock_service = AsyncMock()
        mock_service.get_user_by_id = AsyncMock(return_value={"id": 1})
        mock_service.get_account_for_user = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await get_balance_fn(1)
                result_dict = json.loads(result)

                assert "error" in result_dict
                assert "account" in result_dict["error"].lower()

    @pytest.mark.asyncio
    async def test_get_balance_success(self):
        """Test get_balance returns balance successfully."""
        from datetime import datetime

        tools = list(mcp._tool_manager._tools.values())
        get_balance_tool = next(t for t in tools if t.name == "get_balance")
        get_balance_fn = get_balance_tool.fn

        mock_user = MagicMock()
        mock_account = MagicMock()
        mock_account.id = 1
        mock_account.updated_at = datetime.fromisoformat("2025-12-07T10:00:00")

        mock_service = AsyncMock()
        mock_service.get_user_by_id = AsyncMock(return_value=mock_user)
        mock_service.get_account_for_user = AsyncMock(return_value=mock_account)
        mock_service.calculate_user_balance = AsyncMock(return_value=1000.50)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await get_balance_fn(1)
                result_dict = json.loads(result)

                assert "error" not in result_dict
                assert result_dict["user_id"] == 1
                assert result_dict["account_id"] == 1
                assert result_dict["balance"] == 1000.50
                assert result_dict["currency"] == "USD"

    @pytest.mark.asyncio
    async def test_get_balance_exception_handling(self):
        """Test get_balance handles exceptions gracefully."""
        tools = list(mcp._tool_manager._tools.values())
        get_balance_tool = next(t for t in tools if t.name == "get_balance")
        get_balance_fn = get_balance_tool.fn

        mock_service = AsyncMock()
        mock_service.get_user_by_id = AsyncMock(side_effect=RuntimeError("DB error"))

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await get_balance_fn(1)
                result_dict = json.loads(result)

                assert "error" in result_dict


class TestListBillsTool:
    """Tests for list_bills MCP tool."""

    @pytest.mark.asyncio
    async def test_list_bills_not_initialized(self):
        """Test list_bills returns error when DB not initialized."""
        tools = list(mcp._tool_manager._tools.values())
        list_bills_tool = next(t for t in tools if t.name == "list_bills")
        list_bills_fn = list_bills_tool.fn

        import src.api.mcp_server as mcp_module

        old_session_maker = mcp_module._session_maker
        mcp_module._session_maker = None

        result = await list_bills_fn(1)
        result_dict = json.loads(result)

        assert "error" in result_dict
        assert "not initialized" in result_dict["error"].lower()

        mcp_module._session_maker = old_session_maker

    @pytest.mark.asyncio
    async def test_list_bills_no_account(self):
        """Test list_bills handles user without account."""
        tools = list(mcp._tool_manager._tools.values())
        list_bills_tool = next(t for t in tools if t.name == "list_bills")
        list_bills_fn = list_bills_tool.fn

        mock_service = AsyncMock()
        mock_service.get_account_for_user = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await list_bills_fn(999)
                result_dict = json.loads(result)

                assert "error" in result_dict
                assert "account" in result_dict["error"].lower()

    @pytest.mark.asyncio
    async def test_list_bills_success(self):
        """Test list_bills returns bills successfully."""
        tools = list(mcp._tool_manager._tools.values())
        list_bills_tool = next(t for t in tools if t.name == "list_bills")
        list_bills_fn = list_bills_tool.fn

        mock_account = MagicMock()
        mock_account.id = 1

        mock_bill1 = MagicMock()
        mock_bill1.bill_id = 1
        mock_bill1.amount = 100.0
        mock_bill1.bill_date = "2025-12-01"
        mock_bill1.bill_type = "electricity"

        mock_service = AsyncMock()
        mock_service.get_account_for_user = AsyncMock(return_value=mock_account)
        mock_service.list_bills_for_user = AsyncMock(return_value=[mock_bill1])

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await list_bills_fn(1)
                result_dict = json.loads(result)

                assert "error" not in result_dict
                assert result_dict["user_id"] == 1
                assert result_dict["account_id"] == 1
                assert len(result_dict["bills"]) == 1
                assert result_dict["bills"][0]["bill_id"] == 1

    @pytest.mark.asyncio
    async def test_list_bills_custom_limit(self):
        """Test list_bills respects custom limit parameter."""
        tools = list(mcp._tool_manager._tools.values())
        list_bills_tool = next(t for t in tools if t.name == "list_bills")
        list_bills_fn = list_bills_tool.fn

        mock_account = MagicMock()
        mock_account.id = 1

        mock_bills = [
            MagicMock(bill_id=i, amount=50.0 * i, bill_date="2025-12-01", bill_type="electricity")
            for i in range(1, 6)
        ]

        mock_service = AsyncMock()
        mock_service.get_account_for_user = AsyncMock(return_value=mock_account)
        mock_service.list_bills_for_user = AsyncMock(return_value=mock_bills)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await list_bills_fn(1, limit=5)
                result_dict = json.loads(result)

                mock_service.list_bills_for_user.assert_called_once_with(1, 5)
                assert len(result_dict["bills"]) == 5

    @pytest.mark.asyncio
    async def test_list_bills_exception_handling(self):
        """Test list_bills handles exceptions gracefully."""
        tools = list(mcp._tool_manager._tools.values())
        list_bills_tool = next(t for t in tools if t.name == "list_bills")
        list_bills_fn = list_bills_tool.fn

        mock_service = AsyncMock()
        mock_service.get_account_for_user = AsyncMock(side_effect=RuntimeError("DB error"))

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.BalanceCalculationService", return_value=mock_service):
                result = await list_bills_fn(1)
                result_dict = json.loads(result)

                assert "error" in result_dict


class TestGetPeriodInfoTool:
    """Tests for get_period_info MCP tool."""

    @pytest.mark.asyncio
    async def test_get_period_info_not_initialized(self):
        """Test get_period_info returns error when DB not initialized."""
        tools = list(mcp._tool_manager._tools.values())
        get_period_info_tool = next(t for t in tools if t.name == "get_period_info")
        get_period_info_fn = get_period_info_tool.fn

        import src.api.mcp_server as mcp_module

        old_session_maker = mcp_module._session_maker
        mcp_module._session_maker = None

        result = await get_period_info_fn(1)
        result_dict = json.loads(result)

        assert "error" in result_dict
        assert "not initialized" in result_dict["error"].lower()

        mcp_module._session_maker = old_session_maker

    @pytest.mark.asyncio
    async def test_get_period_info_not_found(self):
        """Test get_period_info handles missing period."""
        tools = list(mcp._tool_manager._tools.values())
        get_period_info_tool = next(t for t in tools if t.name == "get_period_info")
        get_period_info_fn = get_period_info_tool.fn

        mock_service = AsyncMock()
        mock_service.get_period_info = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await get_period_info_fn(999)
                result_dict = json.loads(result)

                assert "error" in result_dict
                assert "not found" in result_dict["error"].lower()

    @pytest.mark.asyncio
    async def test_get_period_info_success(self):
        """Test get_period_info returns period successfully."""
        tools = list(mcp._tool_manager._tools.values())
        get_period_info_tool = next(t for t in tools if t.name == "get_period_info")
        get_period_info_fn = get_period_info_tool.fn

        mock_period = MagicMock()
        mock_period.period_id = 1
        mock_period.name = "September 2025 - January 2026"
        mock_period.start_date = "2025-09-01"
        mock_period.end_date = "2026-01-31"
        mock_period.is_active = True

        mock_service = AsyncMock()
        mock_service.get_period_info = AsyncMock(return_value=mock_period)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await get_period_info_fn(1)
                result_dict = json.loads(result)

                assert "error" not in result_dict
                assert result_dict["period_id"] == 1
                assert result_dict["name"] == "September 2025 - January 2026"

    @pytest.mark.asyncio
    async def test_get_period_info_exception_handling(self):
        """Test get_period_info handles exceptions gracefully."""
        tools = list(mcp._tool_manager._tools.values())
        get_period_info_tool = next(t for t in tools if t.name == "get_period_info")
        get_period_info_fn = get_period_info_tool.fn

        mock_service = AsyncMock()
        mock_service.get_period_info = AsyncMock(side_effect=RuntimeError("DB error"))

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await get_period_info_fn(1)
                result_dict = json.loads(result)

                assert "error" in result_dict


class TestCreateServicePeriodTool:
    """Tests for create_service_period MCP tool."""

    @pytest.mark.asyncio
    async def test_create_period_not_initialized(self):
        """Test create_service_period returns error when DB not initialized."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        import src.api.mcp_server as mcp_module

        old_session_maker = mcp_module._session_maker
        mcp_module._session_maker = None

        result = await create_period_fn("Test Period", "2025-09-01", "2026-01-31")
        result_dict = json.loads(result)

        assert "error" in result_dict
        assert "not initialized" in result_dict["error"].lower()

        mcp_module._session_maker = old_session_maker

    @pytest.mark.asyncio
    async def test_create_period_invalid_start_date_format(self):
        """Test create_service_period validates start_date format."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        result = await create_period_fn("Test Period", "invalid-date", "2026-01-31")
        result_dict = json.loads(result)

        assert "error" in result_dict

    @pytest.mark.asyncio
    async def test_create_period_invalid_end_date_format(self):
        """Test create_service_period validates end_date format."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        result = await create_period_fn("Test Period", "2025-09-01", "01-31-2026")
        result_dict = json.loads(result)

        assert "error" in result_dict

    @pytest.mark.asyncio
    async def test_create_period_success(self):
        """Test create_service_period creates period successfully."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        mock_period = MagicMock()
        mock_period.id = 1
        mock_period.name = "September 2025 - January 2026"
        mock_period.start_date = date_type(2025, 9, 1)
        mock_period.end_date = date_type(2026, 1, 31)

        mock_service = AsyncMock()
        mock_service.create_period = AsyncMock(return_value=mock_period)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await create_period_fn(
                    "September 2025 - January 2026", "2025-09-01", "2026-01-31"
                )
                result_dict = json.loads(result)

                assert "error" not in result_dict
                assert result_dict["success"] is True
                assert result_dict["period_id"] == 1

    @pytest.mark.asyncio
    async def test_create_period_with_electricity_params(self):
        """Test create_service_period accepts optional electricity parameters."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        mock_period = MagicMock()
        mock_period.id = 2
        mock_period.name = "Test Period"
        mock_period.start_date = date_type(2025, 9, 1)
        mock_period.end_date = date_type(2026, 1, 31)

        mock_service = AsyncMock()
        mock_service.create_period = AsyncMock(return_value=mock_period)

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await create_period_fn(
                    "Test Period",
                    "2025-09-01",
                    "2026-01-31",
                    electricity_start=1000,
                    electricity_rate=0.15,
                )
                result_dict = json.loads(result)

                assert "error" not in result_dict
                assert result_dict["success"] is True

    @pytest.mark.asyncio
    async def test_create_period_validation_error(self):
        """Test create_service_period handles validation errors from service."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        mock_service = AsyncMock()
        mock_service.create_period = AsyncMock(
            side_effect=ValueError("End date must be after start date")
        )

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await create_period_fn("Bad Period", "2026-01-31", "2025-09-01")
                result_dict = json.loads(result)

                assert "error" in result_dict

    @pytest.mark.asyncio
    async def test_create_period_exception_handling(self):
        """Test create_service_period handles exceptions gracefully."""
        tools = list(mcp._tool_manager._tools.values())
        create_period_tool = next(t for t in tools if t.name == "create_service_period")
        create_period_fn = create_period_tool.fn

        mock_service = AsyncMock()
        mock_service.create_period = AsyncMock(side_effect=RuntimeError("DB error"))

        mock_session = AsyncMock()
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        with patch("src.api.mcp_server._session_maker", mock_session_maker):
            with patch("src.api.mcp_server.AsyncServicePeriodService", return_value=mock_service):
                result = await create_period_fn("Test Period", "2025-09-01", "2026-01-31")
                result_dict = json.loads(result)

                assert "error" in result_dict
