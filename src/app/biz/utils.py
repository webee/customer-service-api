class ChannelDomainPacker:
    @staticmethod
    def pack(domain, channel=None):
        return f'{channel}/{domain}' if channel is not None else domain

    @staticmethod
    def unpack(p, default_channel=None):
        return p.split('/', 1) if '/' in p else (default_channel, p)


class TypeMsgPacker:
    @staticmethod
    def is_type_valid(t):
        for c in t:
            if not c.islower():
                return False
        return True

    @staticmethod
    def pack(t, content):
        return f'{t}:{content}'

    @staticmethod
    def unpack(p, default_type=''):
        is_ok = False

        idx = 0
        for i, c in enumerate(p):
            if c == ':':
                is_ok = True
                break

            if c.islower():
                idx = i + 1
                continue

            return default_type, p

        return (p[:idx], p[idx + 1:]) if is_ok else (default_type, p)
