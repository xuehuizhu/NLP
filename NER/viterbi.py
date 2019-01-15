import numpy as np

def run_viterbi(emission_scores, trans_scores, start_scores, end_scores):
    """Run the Viterbi algorithm.

    N - number of tokens (length of sentence)
    L - number of labels

    As an input, you are given:
    - Emission scores, as an NxL array
    - Transition scores (Yp -> Yc), as an LxL array
    - Start transition scores (S -> Y), as an Lx1 array
    - End transition scores (Y -> E), as an Lx1 array

    You have to return a tuple (s,y), where:
    - s is the score of the best sequence
    - y is a size N array of integers representing the best sequence.
    """
    L = start_scores.shape[0]
    assert end_scores.shape[0] == L
    assert trans_scores.shape[0] == L
    assert trans_scores.shape[1] == L
    assert emission_scores.shape[1] == L
    N = emission_scores.shape[0]

    result_table = np.zeros((N, L)).tolist()
    final_tag = 0
    #v[t, i] = maxt' v[t', i-1] x P(t|t') x P(wi|ti)
    #fill in first row
    i = 0
    for j in range(L):
        result_table[i][j] = []
        result_table[i][j].append(start_scores[j] + emission_scores[i][j])
    #fill in other cells
    for i in range(1,N):
        for j in range(L):
            result_table[i][j] = []
            max_value = -np.inf
            for x in range(L):
                temp = result_table[i-1][x][0] + trans_scores[x][j] + emission_scores[i][j]
                if temp > max_value:
                    max_value = temp
                    tag = x
            result_table[i][j].append(max_value)
            result_table[i][j].append(tag)

    #calculate max probability ends with </s>
    score = -np.inf
    for j in range(L):
        temp = result_table[N-1][j][0] + end_scores[j]
        if temp > score:
            score = temp
            final_tag = j
    #get the best sequence
    y = []
    for i in range(N-1, 0, -1):
        y.append(final_tag)
        final_tag = result_table[i][final_tag][1]
    y.append(final_tag)
    y = list(reversed(y))
    return (score, y)
