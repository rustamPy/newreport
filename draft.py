from functools import cache
from math import inf


def solve(coord):
    N = len(coord)

    # [[0, 0], [-2, 0], [1, 2], [-1, 3]]
    #  |𝑥𝑖−𝑥𝑗 + 𝑦𝑖 − 𝑦𝑗 |
    @cache
    def dfs(n, visited):
        if n == N:
            return abs(coord[n][0] - coord[0][0] + coord[n][1] - coord[0][1])
        res = inf
        for i in range(N):
            if not i in visited:
                visited.add(i)
                range = coord[i][0] - coord[i - 1][0] + coord[i][1] - coord[i - 1][1]
                duration = range + dfs(i, visited)

                visited.remove(i)
                res = min(res, duration)
        return res

    visited = {0}
    return dfs(0, visited)


solve([[0, 0], [-2, 0], [1, 2], [-1, 3]])
