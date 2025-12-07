"""Node wrapper to inject runtime context."""

from typing import Dict, Any, Callable
from src.state.models import WorkflowState


class RuntimeContext:
    """Global runtime context for nodes."""
    
    def __init__(self):
        self.checkpoint_store = None
        self.human_review_repo = None
        self._human_decisions = {}  # thread_id -> decision data
    
    def set(self, checkpoint_store, human_review_repo):
        """Set runtime context."""
        self.checkpoint_store = checkpoint_store
        self.human_review_repo = human_review_repo
    
    def set_human_decision(self, thread_id: str, decision_data: dict):
        """Store human decision for a thread."""
        self._human_decisions[thread_id] = decision_data
    
    def get_human_decision(self, thread_id: str) -> dict:
        """Get human decision for a thread."""
        return self._human_decisions.get(thread_id, {})


runtime_context = RuntimeContext()


def wrap_node(node_func: Callable, inject_runtime: bool = False) -> Callable:
    """
    Wrap a node function to inject runtime context.
    
    Args:
        node_func: Original node function
        inject_runtime: Whether to inject runtime context
        
    Returns:
        Wrapped node function
    """
    def wrapped(state: WorkflowState, config: Dict[str, Any] = None) -> Dict[str, Any]:
        # Handle config parameter (may be None or provided by LangGraph)
        if config is None:
            config = {}
        
        # Always create runtime, but only populate if needed
        runtime = {}
        if inject_runtime:
            thread_id = state.get("thread_id")
            runtime = {
                "checkpoint_store": runtime_context.checkpoint_store,
                "human_review_repo": runtime_context.human_review_repo,
                "human_decision": runtime_context.get_human_decision(thread_id) if thread_id else {}
            }
        return node_func(state, config, runtime)
    
    return wrapped

