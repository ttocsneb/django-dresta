import math

from typing import List, Any


def pagify(data: List[Any], page: int, size: int, name: str = 'data') -> dict:
    """
    Convert a list of data into pages of data

    :param data: full data
    :param page: page number
    :param size: page size
    :param name: name of the data

    :return: dictionary of the data
    """

    total = len(data)
    if size <= 0:
        size = -1
        pages = 1
    else:
        pages = math.ceil(total / size)
    page = max(0, min(pages - 1, page))

    if size == -1:
        result = data
    else:
        start = page * size
        end = start + size
        result = data[start:end]

    return {
        name: result,
        'page': page,
        'size': size,
        'pages': pages,
        'total': total
    }
