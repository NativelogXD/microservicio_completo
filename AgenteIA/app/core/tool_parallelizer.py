from typing import List, Dict, Any, Tuple
import asyncio
import logging

try:
    import structlog  # type: ignore
except ImportError:
    class _StructlogShim:
        def get_logger(self, name):
            return logging.getLogger(name)
    structlog = _StructlogShim()  # type: ignore


logger = structlog.get_logger(__name__)


class ToolParallelizer:
    INFO_GATHERING_TOOLS = set()

    def _analyze_tool_dependencies(self, tool_calls: List[Dict]) -> Tuple[List[List[Dict]], List[Dict]]:
        if not tool_calls:
            return ([], [])
        first_batch: List[Dict] = []
        second_batch: List[Dict] = []
        for tc in tool_calls:
            name = tc.get("name") or tc.get("tool_name")
            if name in self.INFO_GATHERING_TOOLS:
                first_batch.append(tc)
            else:
                second_batch.append(tc)
        if not first_batch or not second_batch:
            return ([tool_calls], [])
        return ([first_batch], second_batch)

    async def _execute_tools_parallel(self, tool_calls: List[Dict], execute_func, jwt_token: str = "", group_id: str = "") -> List[Dict[str, Any]]:
        logger.info("executing_tools_parallel", tool_count=len(tool_calls))

        async def _run(tc: Dict):
            name = tc.get("name") or tc.get("tool_name")
            args = dict(tc.get("input") or tc.get("arguments") or {})
            if jwt_token and "jwt_token" not in args:
                args["jwt_token"] = jwt_token
            if group_id and "group_id" not in args:
                args["group_id"] = group_id
            try:
                res = await execute_func(name, args, {})
                return {"tool_name": name, "tool_arguments": args, "tool_result": res, "is_error": False}
            except Exception as e:
                logger.error("tool_execution_failed", tool=name, error=str(e))
                return {"tool_name": name, "tool_arguments": args, "tool_result": {"error": str(e)}, "is_error": True}

        return await asyncio.gather(*[_run(tc) for tc in tool_calls])