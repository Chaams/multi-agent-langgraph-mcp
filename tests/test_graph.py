from src.graph import analyst, build_graph, generator, planner
from src.tools import run_tests


def test_planner_produces_three_scenarios():
    assert len(planner({"ticket": "login"})["plan"]) == 3


def test_generator_creates_one_test_per_scenario():
    plan = planner({"ticket": "login"})["plan"]
    code = generator({"plan": plan})["tests"]
    assert code.count("def test_scenario_") == 3


def test_run_tests_counts_failures():
    result = run_tests("def test_ok():\n    assert True\n\ndef test_ko():\n    assert False\n")
    assert (result["passed"], result["failed"]) == (1, 1)


def test_analyst_flags_failures():
    report = analyst({"results": {"passed": 1, "failed": 2, "total": 3}})["report"]
    assert "ÉCHECS" in report


def test_full_graph_end_to_end():
    out = build_graph().invoke({"ticket": "Connexion valide"})
    assert out["results"]["failed"] == 0
    assert out["report"].startswith("OK")
