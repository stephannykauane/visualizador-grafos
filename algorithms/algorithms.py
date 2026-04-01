def bfs_steps(graph, start):

    if start not in graph.nodes:
        return []
    
    visited = []
    queue = [start]
    steps = []

    
    while queue:
       
        current = queue.pop(0)
  
        steps.append({
            "current": current,
            "current_neighbor": None,
            "visited": list(visited),
            "queue": list(queue),
            "type": "BFS",
            "step_num": len(steps) + 1,
        })
        
   
        neighbors = sorted(list(graph.neighbors(current)))
        
        for neighbor in neighbors:
     
            if neighbor not in visited and neighbor not in queue:
            
                visited.append(neighbor)
                queue.append(neighbor)
                
              
                steps.append({
                    "current": current,
                    "current_neighbor": neighbor,
                    "visited": list(visited),
                    "queue": list(queue),
                    "type": "BFS",
                    "step_num": len(steps) + 1,
                })
    
    return steps


def dfs_steps(graph, start):
    """
    DFS - Explora um caminho até o fim antes de retroceder
    Usa PILHA (Stack) - LIFO
    """
    if start not in graph.nodes:
        return []
    
    visited = []
    stack = [start]
    steps = []
    
    while stack:

        current = stack[-1]
        
    
        if current not in visited:
        
            visited.append(current)
       
            steps.append({
                "current": current,
                "current_neighbor": None,
                "visited": list(visited),
                "queue": list(stack),  
                "type": "DFS",
                "step_num": len(steps) + 1,
            })
        

        neighbors = sorted(list(graph.neighbors(current)))
        found_unvisited = False
        
        for neighbor in neighbors:
            if neighbor not in visited:
 
                steps.append({
                    "current": current,
                    "current_neighbor": neighbor,
                    "visited": list(visited),
                    "queue": list(stack),
                    "type": "DFS",
                    "step_num": len(steps) + 1,
                })
       
                stack.append(neighbor)
                found_unvisited = True
                break
   
        if not found_unvisited:
            stack.pop()
            
         
            if stack:
                steps.append({
                    "current": stack[-1],
                    "current_neighbor": None,
                    "visited": list(visited),
                    "queue": list(stack),
                    "type": "DFS",
                    "step_num": len(steps) + 1,
                })
    
    return steps