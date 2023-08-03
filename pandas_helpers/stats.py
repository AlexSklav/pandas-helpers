import itertools
import pandas as pd
from scipy.stats import wilcoxon
from typing import Dict, Optional


def convert_pvalue_to_asterisks(pvalue):
    if pvalue <= 0.0001:
        return "****"
    elif pvalue <= 0.001:
        return "***"
    elif pvalue <= 0.01:
        return "**"
    elif pvalue <= 0.05:
        return "*"
    else:
        return "ns"


def significance_comparison(data_vectors: Dict, n_elements: Optional[int] = 5) -> pd.DataFrame:
    """
    Perform pairwise Wilcoxon sign-rank test on each paired combination of
    placer algorithms.

    Parameters:
    data_vectors (dict): A dictionary of data vectors for each algorithm.
    n_elements (int): Require at least $N$ elements in each vector, where $N = 5$

    Returns:
    pd.DataFrame: A DataFrame containing the results of the Wilcoxon test.
                  Columns: 'A', 'B', 'p-value', 'significant'.
    """
    wilcoxon_results = []
    for (k1, v1), (k2, v2) in itertools.combinations(data_vectors.items(), 2):
        min_atoms = min(len(v1), len(v2))

        if min_atoms < n_elements:
            raise ValueError(f"At least {n_elements} elements are required in each vector."
                             f" ({k1} has {len(v1)}, {k2} has {len(v2)})")

        if len(v1) > min_atoms:
            print(f"[warning] {k1} has more elements than {k2}."
                  f" Only using first {min_atoms} elements from {k1}")
            v1 = v1[:min_atoms]
        elif len(v2) > min_atoms:
            print(f"[warning] {k2} has more elements than {k1}."
                  f" Only using first {min_atoms} elements from {k2}")
            v2 = v2[:min_atoms]

        p_value = wilcoxon(v1, v2).pvalue
        wilcoxon_results.append((k1, k2, p_value, p_value < 0.05, convert_pvalue_to_asterisks(p_value)))

    p_values = pd.DataFrame(wilcoxon_results, columns=['A', 'B', 'p-value', 'significant', 'asterisks'])
    return p_values
