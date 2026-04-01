def bfs_steps(graph, start):
    if start not in graph.nodes:
        return []
    visited = []
    queue = [start]
    queued = [start]
    steps = []
    
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
    
            neighbors = sorted(list(graph.neighbors(node)))
            new_neighbors = [n for n in neighbors if n not in visited and n not in queue]
            for n in new_neighbors:
                if n not in queued:
                    queue.append(n)
                    queued.append(n)
            steps.append({
                "current": node,
                "visited": list(visited),
                "queue": list(queue),
                "type": "BFS",
                "step_num": len(steps) + 1,
            })
    return steps


def dfs_steps(graph, start):
    if start not in graph.nodes:
        return []
    visited = []
    stack = [start]
    steps = []
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.append(node)

            neighbors = sorted(list(graph.neighbors(node)))

            new_neighbors = [n for n in reversed(neighbors) if n not in visited]
            for n in new_neighbors:
                stack.append(n)
            steps.append({
                "current": node,
                "visited": list(visited),
                "queue": list(stack),
                "type": "DFS",
                "step_num": len(steps) + 1,
            })
    return steps