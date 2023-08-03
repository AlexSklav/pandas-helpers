import six
import json

import pandas as pd

from typing import Dict, Any, List, Union, Optional

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


def flatten_dict_to_dataframe(data_frames_by_label: Dict[str, pd.DataFrame], label_name: str = 'label') -> pd.DataFrame:
    """
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
    """
    return pd.concat(data_frames_by_label, names=[label_name]).reset_index(level=0).reset_index(drop=True)


class PandasJsonEncoder(json.JSONEncoder):
    """
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
    """

    def default(self, obj: Any) -> Dict:
        """
        Parameters
        ----------
        obj : object
            Object to serialize to JSON.
        """
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            value = {'index': obj.index.to_list(),
                     'values': obj.values.tolist(),
                     }
            if isinstance(obj, pd.DataFrame):
                value['type'] = 'DataFrame'
                value['dtypes'] = [str(i) for i in obj.dtypes.to_list()]
                value['columns'] = obj.columns.to_list()

                if isinstance(obj.columns, pd.MultiIndex):
                    value['column_names'] = list(obj.columns.names)
                    value['multi_columns'] = True
                else:
                    if obj.columns.name:
                        value['column_name'] = list(obj.columns.names)
                    value['multi_columns'] = False
            else:
                value['type'] = 'Series'
                value['dtype'] = str(obj.dtype)
                if obj.name:
                    value['name'] = obj.name

            if isinstance(obj.index, pd.MultiIndex):
                value['index_dtypes'] = [str(i) for i in obj.index.dtypes.to_list()]
                value['index_names'] = list(obj.index.names)
                value['multi_index'] = True
            else:
                value['index_dtype'] = str(obj.index.dtype)
                if obj.index.name:
                    value['index_name'] = obj.index.name
                value['multi_index'] = False

            return value
        else:
            try:
                return {k: getattr(obj, k) for k in dir(obj) if isinstance(getattr(obj, k),
                                                                           (int, float, pd.Series,
                                                                            pd.DataFrame) + six.string_types)}
            except Exception:
                pass
        return super().default(obj)


def pandas_object_hook(obj: Dict[str, Any]) -> Union[pd.DataFrame, Any]:
    """
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
    """
    # Decode `pandas.Series` from `dict` with `index`, `values`, `dtype`
    # and `type="Series"`.
    if obj.get('type') in ['Series', 'DataFrame']:
        if obj.get('multi_index'):
            index = pd.MultiIndex.from_tuples(obj['index'], names=obj['index_names'])
            # TODO Add Support for changing the dtypes of multiIndex
        else:
            index = pd.Index(obj['index'], dtype=obj['index_dtype'], name=obj.get('index_name'))

        if obj.get('type') == 'Series':
            value = pd.Series(obj['values'], index=index, dtype=obj['dtype'], name=obj.get('name'))
        else:
            if obj.get('multi_columns'):
                columns = pd.MultiIndex.from_tuples(obj['columns'], names=obj['column_names'])
                # TODO Add Support for changing the dtypes of multiIndex
            else:
                columns = obj['columns']

            value = pd.DataFrame(obj['values'], index=index, columns=columns)

        return value
    return obj
