import math

import numpy as np


def point_to_line_distance(px, py, x1, y1, x2, y2):
    # Distance from point to single line segment
    line_mag = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if line_mag < 0.00001:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

    u = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1))) / (line_mag ** 2)
    u = np.clip(u, 0, 1)

    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return math.sqrt((px - ix) ** 2 + (py - iy) ** 2)


def point_to_polyline_distance(px, py, polyline):
    # polyline: list of (x, y) tuples
    min_dist = float("inf")
    for i in range(len(polyline) - 1):
        x1, y1 = polyline[i]
        x2, y2 = polyline[i + 1]
        dist = point_to_line_distance(px, py, x1, y1, x2, y2)
        min_dist = min(min_dist, dist)
    return min_dist


def is_point(a):
    return len(a) == 2


def point_line_dist(line, point):
    if is_point(line) and is_point(point):
        return math.sqrt((line[0] - point[0]) ** 2 + (line[1] - point[1]) ** 2)

    if (not is_point(line)) and (not is_point(point)):
        raise NotImplementedError()
    if is_point(line):
        line, point = point, line

    return point_to_polyline_distance(point[0], point[1], line)


def find_nearest_idx(A, B):
    idx_res = list()
    for anc in A:
        min_dist = point_line_dist(anc, B[0])
        min_i = 0
        for i, item in enumerate(B):
            dist = point_line_dist(anc, item)
            if dist <= min_dist:
                min_dist = dist
                min_i = i
        idx_res.append([min_i])
    return idx_res


# def find_nearest_idx(A, B):
#     nn_B = NearestNeighbors(n_neighbors=1, metric=point_line_dist).fit(B)
#     return nn_B.kneighbors(A, return_distance=False)


def matchA2B(A, B):
    # Mutual NN matching
    indices_A_to_B = find_nearest_idx(A, B)
    indices_B_to_A = find_nearest_idx(B, A)

    return [
        (i, j[0]) for i, j in enumerate(indices_A_to_B) if i in indices_B_to_A[j[0]]
    ]


def iterative_matchA2B(A, B, max_dist=None):
    matches = []
    A_indices = list(range(len(A)))
    B_indices = list(range(len(B)))
    while A_indices and B_indices:
        # Get current points
        A_curr = A[A_indices]
        B_curr = B[B_indices]

        curr_matches = matchA2B(A_curr, B_curr)
        # Convert to original indices and store
        for i_curr, j_curr in curr_matches:
            i_orig = A_indices[i_curr]
            j_orig = B_indices[j_curr]
            matches.append((i_orig, j_orig))

        # Remove matched points (remove from end to avoid index shifting)
        A_to_remove = sorted([i_curr for i_curr, _ in curr_matches], reverse=True)
        B_to_remove = sorted([j_curr for _, j_curr in curr_matches], reverse=True)

        for idx in A_to_remove:
            A_indices.pop(idx)
        for idx in B_to_remove:
            B_indices.pop(idx)
    if max_dist:
        matches = [
            [i, j] for i, j in matches if point_line_dist(A[i], B[j]) <= max_dist
        ]
    return matches
