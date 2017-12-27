from typing import Dict, Tuple, List

# types
t_path_label = List[str]
t_path_labels = List[t_path_label]


class LabelType(object):
    UP = 'up'
    SUPER = 'super'
    SELF = 'self'
    MEMBER = 'self.'
    SELF_PLUS = 'self+'
    SELF_PLUS_PLUS = 'self++'
    SUB = 'sub'
    MEMBER_PLUS = 'self.+'
    ALL = 'all'


def false_matcher(path, target):
    return False


matchers = {
    LabelType.UP: lambda path, target: path.startswith(target) and path != target,
    LabelType.SUPER: lambda path, target: path.startswith(target),
    LabelType.SELF: lambda path, target: path == target,
    LabelType.MEMBER: lambda path, target: target.startswith(path + ':'),
    LabelType.SELF_PLUS: lambda path, target: path == target or target.startswith(path + ':'),
    LabelType.SELF_PLUS_PLUS: lambda path, target: target.startswith(path),
    LabelType.SUB: lambda path, target: target.startswith(path + '.'),
    LabelType.MEMBER_PLUS: lambda path, target: target.startswith(path) and path != target,
    LabelType.ALL: lambda path, target: path.startswith(target) or target.startswith(path),
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
