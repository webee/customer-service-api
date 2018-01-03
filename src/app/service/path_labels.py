from typing import Dict, Tuple, List

# types
t_path_label = List[str]
t_path_labels = List[t_path_label]


class LabelType(object):
    UP = 'up'
    SUPER = 'up+'
    ALIAS_SUPER = 'super'
    SELF = 'self'
    MEMBER = 'self.'
    SELF_PLUS = 'self+'
    SELF_PLUS_PLUS = 'self++'
    SUB = 'sub'
    MEMBER_PLUS = 'self.+'
    ALL = 'all'


def false_matcher(*args, **kwargs):
    return False


matchers = {
    LabelType.UP: lambda path, target: path.startswith(target) and path != target,
    LabelType.SUPER: lambda path, target: path.startswith(target),
    LabelType.ALIAS_SUPER: lambda path, target: path.startswith(target),
    LabelType.SELF: lambda path, target: path == target,
    LabelType.MEMBER: lambda path, target: target.startswith(path + ':'),
    LabelType.SELF_PLUS: lambda path, target: path == target or target.startswith(path + ':'),
    LabelType.SELF_PLUS_PLUS: lambda path, target: target.startswith(path),
    LabelType.SUB: lambda path, target: target.startswith(path + '.'),
    LabelType.MEMBER_PLUS: lambda path, target: target.startswith(path) and path != target,
    LabelType.ALL: lambda path, target: path.startswith(target) or target.startswith(path + ':'),
}

ctx_matchers = {
    LabelType.SELF_PLUS: lambda target, uid, path: path.startswith(target),
    LabelType.SELF: lambda target, uid, path: path.startswith(target),
    LabelType.MEMBER: lambda target, uid, path: (path + ':' + uid).startswith(target),
}


def empty_targets_generator(*args, **kwargs):
    return []


ctx_targets_generators = {
    LabelType.SELF_PLUS: lambda uid, path: [path, path + ':' + uid],
    LabelType.SELF: lambda uid, path: [path],
    LabelType.MEMBER: lambda uid, path: [path + ':' + uid],
}


def get_targets(uid, context_labels):
    return [target for type, path in context_labels for target in
            ctx_targets_generators.get(type, empty_targets_generator)(uid, path)]


def targets_match_ctxes(targets: List[str], uid: str, ctxes: t_path_labels):
    return any(target_match_ctxes(target, uid, ctxes) for target in targets)


def target_match_ctxes(target: str, uid: str, ctxes: t_path_labels):
    return any(target_match_ctx(target, uid, ctx[0], ctx[1]) for ctx in ctxes)


def target_match_ctx(target: str, uid: str, type: str, path: str):
    return ctx_matchers.get(type, false_matcher)(target, uid, path)


def scopes_match_ctxes(scopes: t_path_labels, uid: str, ctxes: t_path_labels):
    return any(scopes_match_ctx(scopes, uid, ctx) for ctx in ctxes)


def scopes_match_ctx(scopes: t_path_labels, uid: str, ctx: t_path_label):
    return scopes_match_ctx_path(scopes, uid, ctx[0], ctx[1])


def scopes_match_ctx_path(scopes: t_path_labels, uid: str, type: str, path: str):
    return any(scopes_match_target(scopes, target) for target in
               ctx_targets_generators.get(type, empty_targets_generator)(uid, path))


def scopes_match_target(scopes: t_path_labels, target: str):
    return any(path_match_target(scope[0], scope[1], target) for scope in scopes)


def path_match_target(type: str, path: str, target: str):
    return matchers.get(type, false_matcher)(path, target)
