import numpy as np

def create_transition_matrix(adj_matrix):
    n = len(adj_matrix)
    transition_matrix = np.zeros((n, n))

    for j in range(n):
        out_links = np.sum(adj_matrix[j])
        if out_links == 0:
            transition_matrix[:, j] = 1.0 / n
        else:
            for i in range(n):
                if adj_matrix[j][i]:
                    transition_matrix[i][j] = 1.0 / out_links

    return transition_matrix

def pagerank(adj_matrix, alpha=0.85, max_iter=100, tol=1e-6):
    n = len(adj_matrix)
    M = create_transition_matrix(adj_matrix)
    rank = np.ones(n) / n 
    teleport = np.ones(n) / n

    for iteration in range(max_iter):
        new_rank = alpha * M @ rank + (1 - alpha) * teleport
        if np.linalg.norm(new_rank - rank, 1) < tol:
            break
        rank = new_rank

    return rank

if __name__ == "__main__":
    adj_matrix = [
        [0, 0, 1, 1],
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0]
    ]

    ranks = pagerank(adj_matrix)
    print("PageRank values:", ranks)