"""Structured logging helpers for Langie."""

import structlog
import json
from typing import Dict, Any, Optional
from datetime import datetime


def setup_logger():
    """Setup structured logger."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()


logger = setup_logger()


def log_node_entry(stage_id: str, thread_id: Optional[str], state_snapshot: Dict[str, Any]):
    """Log node entry."""
    logger.info(
        "node_entry",
        stage_id=stage_id,
        thread_id=thread_id,
        timestamp=datetime.utcnow().isoformat(),
        state_keys=list(state_snapshot.keys())
    )


def log_node_exit(stage_id: str, thread_id: Optional[str], output_keys: list, duration_ms: float):
    """Log node exit."""
    logger.info(
        "node_exit",
        stage_id=stage_id,
        thread_id=thread_id,
        output_keys=output_keys,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat()
    )


def log_bigtool_selection(capability: str, pool: list, selected_tool: str, reason: Optional[str] = None):
    """Log Bigtool selection."""
    logger.info(
        "bigtool_selection",
        capability=capability,
        candidate_pool=pool,
        selected_tool=selected_tool,
        reason=reason or "default_selection",
        timestamp=datetime.utcnow().isoformat()
    )


def log_mcp_call(server: str, ability: str, success: bool, duration_ms: Optional[float] = None, error: Optional[str] = None):
    """Log MCP client call."""
    logger.info(
        "mcp_call",
        server=server,
        ability=ability,
        success=success,
        duration_ms=duration_ms,
        error=error,
        timestamp=datetime.utcnow().isoformat()
    )


def log_checkpoint_created(checkpoint_id: str, invoice_id: str, reason: str, thread_id: str):
    """Log checkpoint creation."""
    logger.info(
        "checkpoint_created",
        checkpoint_id=checkpoint_id,
        invoice_id=invoice_id,
        reason=reason,
        thread_id=thread_id,
        timestamp=datetime.utcnow().isoformat()
    )


def log_human_decision(checkpoint_id: str, decision: str, reviewer_id: str):
    """Log human decision."""
    logger.info(
        "human_decision",
        checkpoint_id=checkpoint_id,
        decision=decision,
        reviewer_id=reviewer_id,
        timestamp=datetime.utcnow().isoformat()
    )


def log_resume_event(thread_id: str, from_stage: str, to_stage: str, checkpoint_id: str):
    """Log workflow resume."""
    logger.info(
        "resume_event",
        thread_id=thread_id,
        from_stage=from_stage,
        to_stage=to_stage,
        checkpoint_id=checkpoint_id,
        timestamp=datetime.utcnow().isoformat()
    )


def log_state_update(stage_id: str, updates: Dict[str, Any]):
    """Log state updates."""
    logger.debug(
        "state_update",
        stage_id=stage_id,
        updates=updates,
        timestamp=datetime.utcnow().isoformat()
    )


def log_error(stage_id: str, error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log error."""
    logger.error(
        "error",
        stage_id=stage_id,
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        timestamp=datetime.utcnow().isoformat(),
        exc_info=True
    )

