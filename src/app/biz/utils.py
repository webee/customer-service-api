
class TypeMsgPacker:
    @staticmethod
    def is_type_valid(t):
        for c in t:
            if not c.islower():
                return False
        return True

    @staticmethod
    def pack(t, msg):
        return '%s:%s' % (t, msg)

    @staticmethod
    def unpack(p):
        is_ok = False

        idx = 0
        for i, c in enumerate(p):
            if c == ':':
                is_ok = True
                break

            if c.islower():
                idx = i + 1
                continue

            return None

        return p[:idx] if is_ok else None
