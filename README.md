# Graph_CSP_Project
# 🎨 Graph Coloring via CSP

This project implements a **CSP solver** for the Graph Coloring problem using:
- Backtracking
- MRV (Minimum Remaining Values)
- LCV (Least Constraining Value)
- AC-3 (Arc Consistency)
- Trail-based undo for domain restoration

## Input format
- First line: `colors=<k>` (integer k ≥ 1)
- Remaining lines: `u,v` (undirected edges)
- Ignore blank lines and lines starting with `#`

Example:  colors=3
1,2
2,3
3,1
3,4              
SOLUTION: {1: 1, 2: 2, 3: 3, 4: 1}

## How to run
Create a virtual environment (optional) and run:
```bash
python graph_csp.py csp_small.txt
python graph_csp.py csp_tight.txt
