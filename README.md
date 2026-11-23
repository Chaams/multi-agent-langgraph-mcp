# multi-agent-langgraph-mcp

Système **multi-agents** orchestré avec **LangGraph** et exposé via **MCP** :

```
ticket ─► planner ─► generator ─► runner ─► analyst ─► rapport
                                    ▲
                      (optionnel) validation humaine avant exécution
```

- `src/graph.py` — graphe LangGraph (un nœud = un agent). `build_graph(human_review=True)` ajoute une
  interruption avant l'exécution : un humain valide les tests générés.
- `src/tools.py` — outil d'exécution de tests, partagé par le graphe et le serveur MCP.
- `src/mcp_server.py` — serveur MCP (`execute_pytest`, `generate_and_run`) utilisable depuis Claude ou un IDE.
- Les agents sont déterministes par défaut (aucune clé API). Branchez un LLM dans `planner` et `generator`.

```bash
pip install -r requirements.txt
pytest -v
python -m src.graph        # lance le graphe sur un ticket d'exemple
python -m src.mcp_server   # démarre le serveur MCP (stdio)
```

Déclarer le serveur dans un client MCP :

```json
{ "mcpServers": { "qa-agents": { "command": "python", "args": ["-m", "src.mcp_server"] } } }
```
