from typing import Dict, Tuple, List

t_path_label = List[List[str]]

LT_SUPER = str(0b10)
LT_SELF = str(0b00)
LT_SUB = str(0b01)
LT_ALL = str(0b11)

false_matcher = lambda path, target: False
matchers = {
    LT_SUPER: lambda path, target: path.startswith(target),
    LT_SELF: lambda path, target: path == target,
    LT_SUB: lambda path, target: target.startswith(path),
    LT_ALL: lambda path, target: path.startswith(target) or target.startswith(path),
}


def path_match_target(type: str, path: str, target: str):
    return matchers.get(type, false_matcher)(path, target)


def scopes_match_ctxes(scopes: t_path_label, uid: str, ctxes: t_path_label):
    pass
