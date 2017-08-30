import pandas as pd
import numpy as np

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def flatten_dict_to_dataframe(data_frames_by_label, label_name='label'):
    '''
    Given a dictionary-like container containing `pandas.DataFrame` instances,
    join all data-frames together into a single data-frame, prepended with an
    additional column containing the dictionary key corresponding to the
    dictionary key each row originated from.

    For example:

    >>> data_frames_by_label = {'A': pd.DataFrame({'a': range(3), 'b': range(3, 6), 'c': range(6, 9)}),
                                'B': pd.DataFrame({'a': range(3), 'b': range(3, 6), 'c': range(6, 9)})}
    >>> for k, v in data_frames_by_label.iteritems():
        print '# %s #' % k
        print v
        print '-' * 15
    ...
    # A #
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8
    ---------------
    # B #
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8
    ---------------
    >>> flatten_dict_to_dataframe(data_frames_by_label)
      label  a  b  c
    0     A  0  3  6
    1     A  1  4  7
    2     A  2  5  8
    3     B  0  3  6
    4     B  1  4  7
    5     B  2  5  8
    '''
    label_len = max([len(k) for k in data_frames_by_label.keys()])
    data_array = np.array([(label, ) + tuple(d)
                           for label, df in data_frames_by_label
                           .iteritems()
                           for field, d in df.iterrows()],
                          dtype=zip([label_name, ]
                                    + list(df.keys()),
                                    ('S%d' % label_len, )
                                    + tuple(df.dtypes)))
    return pd.DataFrame(data_array)
