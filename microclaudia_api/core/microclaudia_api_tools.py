# !/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: URL Module Imports
from urllib.parse import urlencode


def is_sortable(sort_by: str | None = None) -> bool:
    """
    This function, will check whether the given sortBy field is supported by the MicroClaudia API.
    :param sort_by: Requested sort field name.
    :return: True if sort_by is one of the allowed fields; False otherwise (prints a warning).
    """
    if sort_by in ('info.computer_name', 'computerName', 'info.os.caption', 'updated', 'version'):
        return True
    print(
        '[ Warning ]: info.computer_name, computerName, info.os.caption, '
        'updated or version, sortBy will be ignored'
    )
    return False


def sort_agents(url: str, sort_by: str | None = None) -> str:
    """
    This function, will append a sortBy query parameter to a MicroClaudia request URL when valid.
    :param url: Base request URL.
    :param sort_by: Field name to sort by.
    :return: URL unchanged or with &sortBy= appended.
    """
    if sort_by is not None and is_sortable(sort_by):
        return f'{url}&sortBy={sort_by}'
    return url


def is_orderable(sort_by: str | None = None) -> bool:
    """
    This function, will check whether the given orderBy value is asc or desc.
    :param sort_by: Requested sort direction (parameter name is legacy; value is order direction).
    :return: True for asc or desc; False otherwise (prints a warning).
    """
    if sort_by in ('asc', 'desc'):
        return True
    print('[ Warning ]: asc, desc, orderBy will be ignored')
    return False


def order_agents(url: str, order_by: str | None = None) -> str:
    """
    This function, will append an orderBy query parameter to a MicroClaudia request URL when valid.
    :param url: Base request URL.
    :param order_by: Sort direction, asc or desc.
    :return: URL unchanged or with &orderBy= appended.
    """
    if order_by is not None and is_orderable(order_by):
        return f'{url}&orderBy={order_by}'
    return url


def add_query_params(url: str, **params: object) -> str:
    """
    This function, will append non-None, URL-encoded query parameters to a URL.
    :param url: Base request URL.
    :param params: Query parameter names and values.
    :return: URL unchanged or with the provided query parameters appended.
    """
    _values: dict = {key: value for key, value in params.items() if value is not None}
    return f"{url}{'&' if '?' in url else '?'}{urlencode(_values)}" if _values else url


def filter_agents(url: str, filter_by: str | list[str] | None = None) -> str:
    """
    This function, will append a filter query parameter for agent tag filtering when a tag is provided.
    :param url: Base request URL.
    :param filter_by: Tag name or list of tags (only the first tag is used).
    :return: URL unchanged or with the filter query parameter appended.
    """
    if isinstance(filter_by, list):
        if not filter_by:
            return url
        print('[ Warning ]: only the main tag will be applied, api does not support multiple tag filtering')
        filter_by = filter_by[0]
    return add_query_params(url, filter=filter_by)
