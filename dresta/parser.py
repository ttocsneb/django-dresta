"""
Parsers for api related inputs.
"""
import re

from django.http import QueryDict


def parseQueryDict(querydict: QueryDict) -> dict:
    """
    Parse a queryDict into a dictionary

    :param querydict: querydict

    :return: parsed querydict
    """
    parsed = dict()

    def set_node(root, nodes, value):
        if len(nodes) == 1:
            root[nodes[0]] = value
            return
        if not nodes:
            return
        if nodes[0] not in root or not isinstance(root[nodes[0]], dict):
            root[nodes[0]] = dict()
        set_node(root[nodes[0]], nodes[1:], value)

    for k, v in querydict.lists():
        key = k.split('[', 1)[0]
        sub_keys = re.findall(r"\[(.*?)\]", k)
        keys = [key] + sub_keys
        set_node(parsed, keys, v)

    return parsed
