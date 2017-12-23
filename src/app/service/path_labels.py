from typing import Dict, Tuple, List

# types
t_path_label = List[str]
t_path_labels = List[t_path_label]

# label type
LT_SUPER = str(0b10)
LT_SELF = str(0b00)
LT_SUB = str(0b01)
LT_ALL = str(0b11)


def false_matcher(path, target):
    return False


matchers = {
    LT_SUPER: lambda path, target: path.startswith(target),
    LT_SELF: lambda path, target: path == target,
    LT_SUB: lambda path, target: target.startswith(path),
    LT_ALL: lambda path, target: path.startswith(target) or target.startswith(path),
}


def scopes_match_ctxes(scopes: t_path_labels, uid: str, ctxes: t_path_labels):
    return any(scopes_match_ctx(scopes, uid, ctx) for ctx in ctxes)


def scopes_match_ctx(scopes: t_path_labels, uid: str, ctx: t_path_label):
    return scopes_match_ctx_path(scopes, uid, ctx[0], ctx[1])


def scopes_match_ctx_path(scopes: t_path_labels, uid: str, type: str, path: str):
    if type == LT_SELF:
        return scopes_match_target(scopes, path) or scopes_match_target(scopes, path + ':' + uid)
    elif type == LT_SUB:
        return scopes_match_target(scopes, path + ':' + uid)
    return False


def scopes_match_target(scopes: t_path_labels, target: str):
    return any(path_match_target(scope[0], scope[1], target) for scope in scopes)


def path_match_target(type: str, path: str, target: str):
    return matchers.get(type, false_matcher)(path, target)
