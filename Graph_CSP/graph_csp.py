import sys
from collections import deque, defaultdict


def parse_input(filename):
    k = None
    edges = set()
    vertices = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if line.lower().startswith('colors='):
                    try:
                        k = int(line.split('=', 1)[1].strip())
                    except Exception:
                        print('failure')
                        sys.exit(0)
                else:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) != 2:
                        continue
                    try:
                        u = int(parts[0])
                        v = int(parts[1])
                    except ValueError:
                        continue
                 
                    if u == v:
                        print('failure')
                        sys.exit(0)
                    a, b = (u, v) if u <= v else (v, u)
                    edges.add((a, b))
                    vertices.add(a)
                    vertices.add(b)
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(1)

    if k is None:
        print('failure')
        sys.exit(0)

    adj = defaultdict(list)
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)

    for v in adj:
        adj[v] = sorted(set(adj[v]))

    variables = sorted(vertices)
    return k, variables, adj


def revise(X, Y, domains, adj, trail):
    """
    Revise domain of X with respect to Y under constraint X != Y.
    Remove any value x in Dom[X] that has no supporting y in Dom[Y].
    Record pruned pairs to trail (list) as (X, value).
    Return True if domain of X was revised, False otherwise.
    """
    revised = False
    domX = domains[X]
    domY = domains[Y]
    to_remove = []
    for x in list(domX):
        if len(domY) == 1 and next(iter(domY)) == x:
            to_remove.append(x)
    if to_remove:
        for val in to_remove:
            domains[X].remove(val)
            trail.append((X, val))
        revised = True
    return revised

def ac3(queue, domains, adj, trail):
    """
    AC-3 algorithm.
    queue: deque of (Xi, Xj) arcs
    Modifies domains in-place and appends pruned pairs to trail.
    Returns True if no domain became empty; False otherwise.
    """
    while queue:
        Xi, Xj = queue.popleft()
        if revise(Xi, Xj, domains, adj, trail):
            if len(domains[Xi]) == 0:
                return False
            for Xk in adj.get(Xi, []):
                if Xk != Xj:
                    queue.append((Xk, Xi))
    return True


def select_unassigned_variable(domains, assignment):
    """
    MRV: choose unassigned variable with smallest domain size.
    Tie-breaker: smallest variable id (deterministic).
    """
    candidates = []
    for var, dom in domains.items():
        if var not in assignment:
            candidates.append((len(dom), var))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]

def order_domain_values(var, domains, adj, assignment):
    """
    LCV: for each value, compute how many values it would eliminate from
    neighbors' domains. Return values sorted by increasing elimination.
    """
    counts = []
    domain = sorted(domains[var])
    for val in domain:
        eliminated = 0
        for nb in adj.get(var, []):
            if nb in assignment:
                continue
            if val in domains[nb]:
                eliminated += 1
        counts.append((eliminated, val))
    counts.sort()
    return [val for (_, val) in counts]

def backtrack(domains, adj, assignment, trail):
    if len(assignment) == len(domains):
        return True

    var = select_unassigned_variable(domains, assignment)
    if var is None:
        return False

    for value in order_domain_values(var, domains, adj, assignment):
        trail_snapshot = len(trail)
        other_values = [v for v in list(domains[var]) if v != value]
        for v in other_values:
            domains[var].remove(v)
            trail.append((var, v))
        assignment[var] = value

        queue = deque()
        for nb in adj.get(var, []):
            queue.append((nb, var))
        consistent = ac3(queue, domains, adj, trail)
        if consistent:
            empty_found = any(len(domains[x]) == 0 for x in domains)
            if not empty_found:
                result = backtrack(domains, adj, assignment, trail)
                if result:
                    return True

        while len(trail) > trail_snapshot:
            v, val = trail.pop()
            if val not in domains[v]:
                domains[v].add(val)
        del assignment[var]

    return False

def solve_graph_coloring(k, variables, adj):
    domains = {}
    for v in variables:
        domains[v] = set(range(1, k+1))

    assignment = {}
    trail = []

    queue = deque()
    for Xi in variables:
        for Xj in adj.get(Xi, []):
            queue.append((Xi, Xj))
    ok = ac3(queue, domains, adj, trail)
    if not ok:
        return None

    for v in domains:
        if len(domains[v]) == 0:
            return None

    success = backtrack(domains, adj, assignment, trail)
    if not success:
        return None

    for v in variables:
        if v not in assignment:
            if len(domains[v]) >= 1:
                assignment[v] = min(domains[v])
            else:
                return None
    return assignment

def generate_tests():
    small = """# small test (3-colorable)
colors=3
1,2
2,3
3,1
3,4
"""
    tight = """# tight test (triangle with 2 colors -> unsolvable)
colors=2
1,2
2,3
3,1
"""
    with open('csp_small.txt', 'w', encoding='utf-8') as f:
        f.write(small)
    with open('csp_tight.txt', 'w', encoding='utf-8') as f:
        f.write(tight)
    print('Generated csp_small.txt and csp_tight.txt')


def main():
    if len(sys.argv) < 2:
        print('Usage: python graph_csp.py inputfile')
        sys.exit(1)
    if sys.argv[1] == '--gen-tests':
        generate_tests()
        sys.exit(0)

    filename = sys.argv[1]
    k, variables, adj = parse_input(filename)

    if not variables:
        print('SOLUTION: {}')
        sys.exit(0)

    solution = solve_graph_coloring(k, variables, adj)
    if solution is None:
        print('failure')
    else:
        ordered = {v: solution[v] for v in sorted(solution.keys())}
        print('SOLUTION: ' + str(ordered))

if __name__ == '__main__':
    main()
