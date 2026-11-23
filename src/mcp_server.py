"""Serveur MCP exposant les outils de QA à n'importe quel client MCP (Claude, IDE, agents…).

Lancer :  python -m src.mcp_server
"""
from mcp.server.fastmcp import FastMCP

from .graph import build_graph
from .tools import run_tests

mcp = FastMCP("qa-agents")


@mcp.tool()
def execute_pytest(code: str) -> dict:
    """Exécute du code de test pytest et renvoie le nombre de tests réussis/échoués."""
    return run_tests(code)


@mcp.tool()
def generate_and_run(ticket: str) -> str:
    """Lance le graphe multi-agents sur un ticket (plan -> tests -> exécution -> rapport)."""
    return build_graph().invoke({"ticket": ticket})["report"]


if __name__ == "__main__":
    mcp.run()
