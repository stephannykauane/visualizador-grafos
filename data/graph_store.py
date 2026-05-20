from services.graph_service import GraphService

graph_service = GraphService()

state = {
    "selected_node": None,
    "selected_edge": None,
    "last_position": {"x": 300, "y": 250},
    "algo_steps": [],
    "algo_index": 0,
    "running_algo": None,
    "auto_running": False,
    "visited_sequence": None,
    "maxflow_source": None,
    "maxflow_sink": None,
    "_pending_completion": False,
    "_mf_validation_error": False,
}