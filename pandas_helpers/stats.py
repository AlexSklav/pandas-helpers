import itertools

from scipy.stats import wilcoxon
import pandas as pd


def significance_comparison(data_vectors):
    # Perform pairwise Wilcoxon sign-rank test on each paired combination of
    # placer algorithms.
    wilcoxon_results = []
    for (k1, v1), (k2, v2) in itertools.combinations(data_vectors.items(), 2):
        min_atoms = min(len(v1), len(v2))

        # Require at least $N$ elements in each vector, where $N = 5$.
        # TODO: $N$ should likely be configurable...
        N = 5
        if min_atoms < N:
            raise ValueError('At least %d elements are required in each '
                             'vector. (%s has %d, %s has %d)' % (N, k1,
                                                                 len(v1), k2,
                                                                 len(v2)))
        if len(v1) > min_atoms:
            print ('[warning] %s has more elements than %s.  Only using first '
                   '%d elements from %s' % (k1, k2, min_atoms, k1))
            v1 = v1[:min_atoms]
        elif len(v2) > min_atoms:
            print ('[warning] %s has more elements than %s.  Only using first '
                   '%d elements from %s' % (k2, k1, min_atoms, k2))
            v2 = v2[:min_atoms]
        p_value = wilcoxon(v1, v2)[-1]
        wilcoxon_results.append((k1, k2, p_value, p_value < 0.05))

    p_values = pd.DataFrame(wilcoxon_results, columns=('A', 'B', 'p-value',
                                                       'significant'))
    return p_values
