def build_function_index(functions):
    """
    Map function name → list of function objects
    """
    index = {}

    for f in functions:
        name = f["name"]
        if name not in index:
            index[name] = []
        index[name].append(f)

    return index


def build_call_graph(functions):
    """
    Build call graph with cross-file resolution.
    """
    graph = {}
    index = build_function_index(functions)

    # Initialize nodes
    for f in functions:
        graph[f["name"]] = {
            "calls": [],
            "called_by": []
        }

    # Resolve calls
    for f in functions:
        caller = f["name"]

        for called_name in f.get("calls", []):
            if called_name in index:
                if called_name not in graph[caller]["calls"]:
                    graph[caller]["calls"].append(called_name)

    # Reverse edges
    for caller, data in graph.items():
        for callee in data["calls"]:
            if callee in graph:
                if caller not in graph[callee]["called_by"]:
                    graph[callee]["called_by"].append(caller)

    return graph


def get_function_context(functions, target):
    """
    Get call relationships for a function.
    """
    graph = build_call_graph(functions)

    if target not in graph:
        return None

    return graph[target]

def get_multi_hop_calls(graph, start, max_depth=2):
    """
    Perform depth-limited DFS to get multi-hop call chains.

    Returns:
        list of (depth, function_name)
    """
    result = []
    visited = set()

    def dfs(node, depth):
        if depth > max_depth or node in visited:
            return

        visited.add(node)

        for callee in graph.get(node, {}).get("calls", []):
            result.append((depth, callee))
            dfs(callee, depth + 1)

    dfs(start, 1)
    return result

def get_multi_hop_callers(graph, start, max_depth=2):
    """
    Traverse reverse edges (who calls this function)
    """
    result = []
    visited = set()

    def dfs(node, depth):
        if depth > max_depth or node in visited:
            return

        visited.add(node)

        for caller in graph.get(node, {}).get("called_by", []):
            result.append((depth, caller))
            dfs(caller, depth + 1)

    dfs(start, 1)
    return result
