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
}