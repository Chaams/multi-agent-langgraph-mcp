"""Système multi-agents LangGraph : planner -> generator -> runner -> analyst.

Chaque agent est un nœud du graphe. Ici, les nœuds sont déterministes pour que le
projet tourne sans clé API ; pour brancher un LLM, remplacez le corps de `planner`
et `generator` par un appel à votre modèle (voir `llm_hook`).

Le graphe s'arrête avant l'agent « analyst » si `human_review` est activé
(interrupt) : un humain valide les tests générés avant toute exécution.
"""
from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .tools import run_tests


class QAState(TypedDict, total=False):
    ticket: str
    plan: list[str]
    tests: str
    results: dict
    report: str


# Point d'extension : remplacez par un vrai appel LLM (prompt -> texte).
llm_hook: Callable[[str], str] | None = None


def planner(state: QAState) -> QAState:
    """Transforme un ticket en liste de scénarios de test."""
    ticket = state["ticket"]
    plan = [f"Cas nominal : {ticket}", f"Cas limite : {ticket} avec valeur vide", f"Cas d'erreur : {ticket} non autorisé"]
    return {"plan": plan}


def generator(state: QAState) -> QAState:
    """Génère le code de test pytest correspondant au plan."""
    body = ["def test_scenario_{i}():\n    assert True  # TODO: {s}".format(i=i, s=s) for i, s in enumerate(state["plan"], 1)]
    return {"tests": "\n\n".join(body)}


def runner(state: QAState) -> QAState:
    """Exécute les tests via l'outil (le même que celui exposé par le serveur MCP)."""
    return {"results": run_tests(state["tests"])}


def analyst(state: QAState) -> QAState:
    r = state["results"]
    verdict = "OK" if r["failed"] == 0 else "ÉCHECS À ANALYSER"
    return {"report": f"{verdict} — {r['passed']} réussis, {r['failed']} échoués sur {r['total']} tests."}


def build_graph(human_review: bool = False):
    g = StateGraph(QAState)
    g.add_node("planner", planner)
    g.add_node("generator", generator)
    g.add_node("runner", runner)
    g.add_node("analyst", analyst)
    g.add_edge(START, "planner")
    g.add_edge("planner", "generator")
    g.add_edge("generator", "runner")
    g.add_edge("runner", "analyst")
    g.add_edge("analyst", END)
    if human_review:
        return g.compile(checkpointer=MemorySaver(), interrupt_before=["runner"])
    return g.compile()


if __name__ == "__main__":
    result = build_graph().invoke({"ticket": "Un utilisateur se connecte avec un mot de passe valide"})
    print(result["report"])
