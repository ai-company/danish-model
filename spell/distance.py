from . import util

base_char_costs = []
base_prev_char_costs = []


def distance(s1, s2, max_dist):
    """
    Damerau-Levenshtein Optimal String Alignment comparison.
    """
    global base_char_costs
    global base_prev_char_costs

    max_dist = int(min(2 ** 31 - 1, max_dist))

    if len(s1) > len(s2):
        s2, s1 = s1, s2

    if len(s2) - len(s1) > max_dist:
        return -1

    l1, l2, start = util.prefix_suffix(s1, s2)

    if l1 == 0:
        return l2 if l2 <= max_dist else -1

    if l2 > len(base_char_costs):
        base_char_costs = [0 for _ in range(l2)]
        base_prev_char_costs = [0 for _ in range(l2)]

    if max_dist < l2:
        return distance_max(
            s1, s2, l1, l2, start, max_dist, base_char_costs, base_prev_char_costs
        )

    return _distance(s1, s2, l1, l2, start, base_char_costs, base_prev_char_costs)


def _distance(s1, s2, l1, l2, start, char_costs, prev_char_costs):
    char_cost = [j + 1 for j in range(l2)]
    char = " "
    current_cost = 0

    for i in range(l1):
        prev_char = char
        char = s1[start + i]
        char2 = " "

        left_char_cost = above_char_cost = i
        next_trans_cost = 0

        for j in range(l2):
            trans_cost = next_trans_cost
            next_trans_cost = prev_char_costs[j]

            prev_char_costs[j] = current_cost = left_char_cost

            left_char_cost = char_costs[j]
            prev_char2 = char2

            char2 = s2[start + j]

            if char != char2:
                if above_char_cost < current_cost:
                    current_cost = above_char_cost
                if left_char_cost < current_cost:
                    current_cost = left_char_cost

                current_cost += 1

            if (
                i != 0
                and j != 0
                and char == prev_char
                and prev_char == char2
                and trans_cost + 1 < current_cost
            ):

                current_cost = trans_cost + 1

            char_costs[j] = above_char_cost = current_cost

    return current_cost


def distance_max(s1, s2, l1, l2, start, max_dist, char_costs, prev_char_costs):
    char_costs = [j + 1 if j < max_dist else max_dist + 1 for j in range(l2)]

    len_diff = l2 - l1
    j_start_off = max_dist - len_diff
    j_start = 0
    j_end = max_dist

    char = " "
    current_cost = 0

    for i in range(l1):
        prev_char = char
        char = s1[start + i]

        char2 = " "
        left_char_cost = above_char_cost = i
        next_trans_cost = 0

        j_start += 1 if i > j_start_off else 0
        j_end += 1 if j_end < l2 else 0

        for j in range(j_start, j_end):
            trans_cost = next_trans_cost
            next_trans_cost = prev_char_costs[j]

            prev_char_costs[j] = current_cost = left_char_cost

            left_char_cost = char_costs[j]

            left_char_cost = char_costs[j]
            prev_char = char2

            char2 = s2[start + j]

            if char != char2:
                if above_char_cost < current_cost:
                    current_cost = above_char_cost
                if left_char_cost < current_cost:
                    current_cost = left_char_cost

                current_cost += 1

                if (
                    i != 0
                    and j != 0
                    and char == prev_char
                    and prev_char == char2
                    and trans_cost + 1 < current_cost
                ):

                    current_cost = trans_cost + 1

            char_costs[j] = above_char_cost = current_cost

        if char_costs[i + len_diff] > max_dist:
            return -1

    return current_cost if current_cost <= max_dist else -1


if __name__ == "__main__":
    while True:
        text = input("> ").split()
        print(distance(text[0], text[1], 3, include_unknown=False))
        print()
