from typing import List, Dict, Any


def _format_tools_section(tools: List[Dict[str, Any]]) -> str:
    formatted = []
    for tool in tools or []:
        name = tool.get('name', 'unknown')
        description = tool.get('description', '')
        parameters = tool.get('parameters', {}) or {}
        required = parameters.get('required', []) or []
        required_str = ', '.join(required) if required else 'ninguno'
        formatted.append(f"<tool name=\"{name}\"><description>{description}</description><required_params>{required_str}</required_params></tool>")
    return '\n'.join(formatted)


def build_system_prompt(group_id: str, jwt_token: str, available_tools: List[Dict[str, Any]]) -> str:
    tools_formatted = _format_tools_section(available_tools)
    return (
        f"<role>Eres un agente MCP inteligente.</role>\n"
        f"<identity>AgenteIA</identity>\n"
        f"<context><authentication>group_id: {group_id}; jwt_token: {jwt_token}</authentication></context>\n"
        f"<capabilities>\n{tools_formatted}\n</capabilities>\n"
        f"<tool_usage_guidelines><execution_rules>Valida parámetros requeridos antes de ejecutar herramientas; pregunta si falta información crítica.</execution_rules></tool_usage_guidelines>\n"
        f"<response_format><constraints>- Respuestas concisas y accionables</constraints></response_format>"
    )