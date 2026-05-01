import heapq

nodes = {
    'A1': (1.1, 1.5), 'A2': (1.1, 1.0), 'A3': (1.1, 0.5),
    'B1': (1.8, 1.5), 'B2': (1.8, 1.0), 'B3': (1.8, 0.5),
    'C1': (2.6, 1.5), 'C2': (2.6, 1.0), 'C3': (2.6, 0.5),
    'D': (3, 1.5),
    'GOAL': (3.7, 1.5)
}

graph = {
    'A1' : {'A2': {'w': 2, 'type': 0}, 'B1': {'w': 1, 'type': 1}},
    'A2' : {'A1': {'w': 2, 'type': 0}, 'A3': {'w': 2, 'type': 0}, 'B2': {'w': 1, 'type': 1}},
    'A3' : {'A2': {'w': 2, 'type': 0}, 'B3': {'w': 1, 'type': 1}},
    'B1' : {'B2': {'w': 2, 'type': 0}, 'C1': {'w': 1, 'type': 1}},
    'B2' : {'B1': {'w': 2, 'type': 0}, 'B3': {'w': 2, 'type': 0}, 'C2': {'w': 1, 'type': 1}},
    'B3' : {'B2': {'w': 2, 'type': 0}, 'C3': {'w': 1, 'type': 1}},
    'C1' : {'D': {'w': 0, 'type': 0}},
    'C2' : {'D': {'w': 0, 'type': 0}},
    'C3' : {'D': {'w': 0, 'type': 0}},
    'D'  : {'GOAL' : {'w':0, 'type': 0}}
}


def get_path(graph, start, end):
    queue = [(0, start, [])]
    visited = set()
    
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        
        if node not in visited:
            visited.add(node)
            path = path + [node]
            
            if node == end:
                return path
            
            for neighbor, data in graph.get(node, {}).items():
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + data['w'], neighbor, path))
    return None

