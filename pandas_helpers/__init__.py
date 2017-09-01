import json

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


class PandasJsonEncoder(json.JSONEncoder):
    '''
    .. versionadded:: 0.2

    Encoder to serialize Panda series and data frames to JSON.

    Example
    -------

    >>> data = pd.Series(range(10))
    >>> df_data = pd.DataFrame([data.copy() for i in xrange(5)])
    >>> combined_dump = json.dumps([df_data, data], cls=PandasJsonEncoder)
    >>> loaded = json.loads(combined_dump, object_hook=pandas_object_hook)
    >>> assert(loaded[0].equals(df_data))
    >>> assert(loaded[1].equals(data))

    See also
    --------

    :func:`pandas_object_hook`
    '''
    def default(self, object_):
        '''
        Parameters
        ----------
        object_ : object
            Object to serialize to JSON.
        '''
        # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
        # TODO Add support for:
        # TODO  - Multi level index
        # TODO  - Multi level columns index
        # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

        # Use `.values.tolist()` since the `tolist()` method of `pandas`
        # objects does not convert `numpy` numeric types to native Python
        # types, whereas `numpy.ndarray.tolist()` does.

        # Encode `pandas.Series` as `dict` with `index`, `values`, `dtype`
        # and `type="Series"`.
        if isinstance(object_, pd.Series):
            value = {'index': object_.index.values.tolist(),
                     'values': object_.values.tolist(),
                     'index_dtype': str(object_.index.dtype),
                     'dtype': str(object_.dtype),
                     'type': 'Series'}
            if object_.index.name:
                value['index_name'] = object_.index.name
            if object_.name:
                value['name'] = object_.name
            return value
        # Encode `pandas.DataFrame` as `dict` with `index`, `values`, and
        # `type="DataFrame"`.
        elif isinstance(object_, pd.DataFrame):
            value = {'index': object_.index.values.tolist(),
                     'values': object_.values.tolist(),
                     'columns': object_.columns.tolist(),
                     'index_dtype': str(object_.index.dtype),
                     'type': 'DataFrame'}
            if object_.index.name:
                value['index_name'] = object_.index.name
            return value
        else:
            try:
                return {k: getattr(object_, k) for k in dir(object_)
                        if isinstance(getattr(object_, k),
                                      (int, float, pd.Series, pd.DataFrame,
                                       str, unicode))}
            except Exception:
                pass
        return super(PandasJsonEncoder, self).default(object_)


def pandas_object_hook(obj):
    '''
    .. versionadded:: 0.2

    Decode custom JSON representations of Pandas series and data frames into
    corresponding Pandas data types.

    Parameters
    ----------
    obj : dict
        JSON object as decoded by the default decoder.

    Example
    -------

    >>> data = pd.Series(range(10))
    >>> df_data = pd.DataFrame([data.copy() for i in xrange(5)])
    >>> combined_dump = json.dumps([df_data, data], cls=PandasJsonEncoder)
    >>> loaded = json.loads(combined_dump, object_hook=pandas_object_hook)
    >>> assert(loaded[0].equals(df_data))
    >>> assert(loaded[1].equals(data))

    See also
    --------

    :class:`PandasJsonEncoder`
    '''
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO Add support for:
    # TODO  - Multi level index
    # TODO  - Multi level columns index
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

    # Decode `pandas.Series` from `dict` with `index`, `values`, `dtype`
    # and `type="Series"`.
    if obj.get('type') == 'Series':
        value = pd.Series(obj['values'], index=np.array(obj['index'],
                                                        dtype=obj
                                                        ['index_dtype']),
                          dtype=obj['dtype'], name=obj.get('name'))
        value.index.name = obj.get('index_name')
        return value
    # Decode `pandas.DataFrame` from `dict` with `index`, `values`,
    # and `type="DataFrame"`.
    elif obj.get('type') == 'DataFrame':
        value = pd.DataFrame(obj['values'],
                             index=np.array(obj['index'],
                                            dtype=obj['index_dtype']),
                             columns=obj['columns'])
        value.index.name = obj.get('index_name')
        return value
    return obj
