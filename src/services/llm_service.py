"""Ollama LLM service with tool-calling for SOSenki bot.

Provides a wrapper around Ollama's async client with:
- Tool definitions matching MCP server schemas
- Role-based tool filtering (user vs admin)
- Auto-injection of user context
- Tool-calling loop for multi-step queries
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

from ollama import AsyncClient

from src.prompts import ADMIN_SYSTEM_PROMPT, USER_SYSTEM_PROMPT
from src.services.balance_service import BalanceCalculationService
from src.services.locale_service import CURRENCY, format_local_datetime
from src.services.period_service import AsyncServicePeriodService

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# Default model if OLLAMA_MODEL not set
DEFAULT_MODEL = "qwen2.5:latest"


# Prompts are loaded from external .prompt.md files via src.prompts module
# Re-export for backward compatibility (deprecated - use src.prompts directly)
SYSTEM_PROMPT = USER_SYSTEM_PROMPT


# ============================================================================
# Tool Definitions (matching MCP server schemas)
# ============================================================================


def _get_balance_tool() -> dict[str, Any]:
    """Tool definition for get_balance."""
    return {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Get current account balance for the user. Returns balance amount and last update time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }


def _list_bills_tool() -> dict[str, Any]:
    """Tool definition for list_bills."""
    return {
        "type": "function",
        "function": {
            "name": "list_bills",
            "description": "List recent bills for the user. Returns bill details including amounts and dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of bills to return (default: 10)",
                    },
                },
                "required": [],
            },
        },
    }


def _get_period_info_tool() -> dict[str, Any]:
    """Tool definition for get_period_info."""
    return {
        "type": "function",
        "function": {
            "name": "get_period_info",
            "description": "Get information about a specific service period by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "period_id": {
                        "type": "integer",
                        "description": "The service period ID to look up",
                    },
                },
                "required": ["period_id"],
            },
        },
    }


def _create_service_period_tool() -> dict[str, Any]:
    """Tool definition for create_service_period (admin only)."""
    return {
        "type": "function",
        "function": {
            "name": "create_service_period",
            "description": "Create a new service period. Admin-only operation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Period name (e.g., 'September 2025 - January 2026')",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Period start date in YYYY-MM-DD format",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Period end date in YYYY-MM-DD format",
                    },
                },
                "required": ["name", "start_date", "end_date"],
            },
        },
    }


def get_user_tools() -> list[dict[str, Any]]:
    """Get tools available to regular users (read-only)."""
    return [
        _get_balance_tool(),
        _list_bills_tool(),
        _get_period_info_tool(),
    ]


def get_admin_tools() -> list[dict[str, Any]]:
    """Get tools available to admins (read + write)."""
    return [
        _get_balance_tool(),
        _list_bills_tool(),
        _get_period_info_tool(),
        _create_service_period_tool(),
    ]


# ============================================================================
# Tool Execution
# ============================================================================


@dataclass
class ToolContext:
    """Context for tool execution."""

    user_id: int
    is_admin: bool
    session: Any  # AsyncSession


async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    ctx: ToolContext,
) -> str:
    """Execute a tool and return the result as JSON string.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from LLM
        ctx: Execution context with user_id and session

    Returns:
        JSON string with tool result or error
    """
    try:
        if tool_name == "get_balance":
            return await _execute_get_balance(ctx)
        elif tool_name == "list_bills":
            limit = arguments.get("limit", 10)
            return await _execute_list_bills(ctx, limit)
        elif tool_name == "get_period_info":
            period_id = arguments.get("period_id")
            if not period_id:
                return json.dumps({"error": "period_id is required"})
            return await _execute_get_period_info(ctx, period_id)
        elif tool_name == "create_service_period":
            if not ctx.is_admin:
                return json.dumps({"error": "Admin access required for this operation"})
            name = arguments.get("name", "")
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")
            return await _execute_create_service_period(ctx, name, start_date, end_date)
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def _execute_get_balance(ctx: ToolContext) -> str:
    """Execute get_balance tool."""
    service = BalanceCalculationService(ctx.session)

    user = await service.get_user_by_id(ctx.user_id)
    if not user:
        return json.dumps({"error": f"User {ctx.user_id} not found"})

    account = await service.get_account_for_user(ctx.user_id)
    if not account:
        return json.dumps({"error": f"No account found for user {ctx.user_id}"})

    balance = await service.calculate_user_balance(ctx.user_id)

    return json.dumps(
        {
            "user_id": ctx.user_id,
            "user_name": user.name,
            "balance": float(balance),
            "currency": CURRENCY,
            "last_updated": (
                format_local_datetime(account.updated_at) if account.updated_at else None
            ),
        }
    )


async def _execute_list_bills(ctx: ToolContext, limit: int) -> str:
    """Execute list_bills tool."""
    service = BalanceCalculationService(ctx.session)

    account = await service.get_account_for_user(ctx.user_id)
    if not account:
        return json.dumps({"error": f"No account found for user {ctx.user_id}"})

    bills = await service.list_bills_for_user(ctx.user_id, limit)

    return json.dumps(
        {
            "user_id": ctx.user_id,
            "bills": [
                {
                    "bill_id": bill.bill_id,
                    "amount": bill.amount,
                    "bill_date": bill.bill_date,
                    "bill_type": bill.bill_type,
                }
                for bill in bills
            ],
        }
    )


async def _execute_get_period_info(ctx: ToolContext, period_id: int) -> str:
    """Execute get_period_info tool."""
    service = AsyncServicePeriodService(ctx.session)
    period_info = await service.get_period_info(period_id)

    if not period_info:
        return json.dumps({"error": f"Period {period_id} not found"})

    return json.dumps(
        {
            "period_id": period_info.period_id,
            "name": period_info.name,
            "start_date": period_info.start_date,
            "end_date": period_info.end_date,
            "active": period_info.is_active,
        }
    )


async def _execute_create_service_period(
    ctx: ToolContext,
    name: str,
    start_date: str,
    end_date: str,
) -> str:
    """Execute create_service_period tool (admin only)."""
    from datetime import date

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as e:
        return json.dumps({"error": f"Invalid date format: {e}. Use YYYY-MM-DD."})

    service = AsyncServicePeriodService(ctx.session)
    try:
        new_period = await service.create_period(start, end, name)
        return json.dumps(
            {
                "success": True,
                "period_id": new_period.id,
                "name": new_period.name,
                "start_date": new_period.start_date.isoformat(),
                "end_date": new_period.end_date.isoformat(),
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# Ollama Service
# ============================================================================


class OllamaService:
    """Async Ollama client with tool-calling support for SOSenki."""

    def __init__(
        self,
        session: Any,
        user_id: int,
        is_admin: bool = False,
        model: str | None = None,
        host: str | None = None,
    ):
        """Initialize Ollama service.

        Args:
            session: AsyncSession for database operations
            user_id: User ID for tool context (auto-injected into tools)
            is_admin: Whether user has admin privileges
            model: Ollama model to use (default from OLLAMA_MODEL env)
            host: Ollama host URL (default from OLLAMA_HOST env or localhost)
        """
        self.session = session
        self.user_id = user_id
        self.is_admin = is_admin
        self.model = model or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
        host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = AsyncClient(host=host)
        self.tool_context = ToolContext(
            user_id=user_id,
            is_admin=is_admin,
            session=session,
        )

    def _get_tools(self) -> list[dict[str, Any]]:
        """Get available tools based on user role."""
        return get_admin_tools() if self.is_admin else get_user_tools()

    def _get_system_prompt(self) -> str:
        """Get system prompt based on user role."""
        return ADMIN_SYSTEM_PROMPT if self.is_admin else USER_SYSTEM_PROMPT

    async def chat(self, user_message: str, max_tool_calls: int = 5) -> str:
        """Process a user message with optional tool calling.

        Implements tool-calling loop:
        1. Send user message with available tools
        2. If LLM requests tool call, execute it and send result back
        3. Repeat until LLM provides final text response or max calls reached

        Args:
            user_message: The user's question or request
            max_tool_calls: Maximum tool calls before forcing response

        Returns:
            Final text response from LLM
        """
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        tools = self._get_tools()
        tool_call_count = 0

        while tool_call_count < max_tool_calls:
            try:
                response = await self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                )
            except Exception as e:
                logger.error(f"Ollama chat error: {e}", exc_info=True)
                return f"Sorry, I encountered an error connecting to the AI service: {e}"

            message = response.message

            # Check if LLM wants to call tools
            if message.tool_calls:
                # Append assistant message with tool calls
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id if hasattr(tc, "id") else f"call_{tool_call_count}",
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in message.tool_calls
                        ],
                    }
                )

                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

                    result = await execute_tool(tool_name, arguments, self.tool_context)

                    # Add tool result to messages
                    messages.append(
                        {
                            "role": "tool",
                            "content": result,
                            "name": tool_name,
                        }
                    )

                    tool_call_count += 1

            else:
                # No tool calls - return final response
                return message.content or "I couldn't generate a response."

        # Max tool calls reached
        logger.warning(f"Max tool calls ({max_tool_calls}) reached for user {self.user_id}")
        return "I've gathered the information but reached my limit. Please try a simpler question."


__all__ = [
    "OllamaService",
    "get_user_tools",
    "get_admin_tools",
    "execute_tool",
    "ToolContext",
]
