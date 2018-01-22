from functools import partial
import sys
import json
from app.biz.utils import TypeMsgPacker, ChannelDomainPacker

SEP = '\t'


def filter_keys(d, keys=None):
    return {k: v for k, v in d.items() if keys is None or k in keys}


filter_funcs = {
    'text': partial(filter_keys, keys={'text'}),
    'file': partial(filter_keys, keys={'url', 'name', 'size'}),
    'image': partial(filter_keys, keys={'url', 'name', 'size', 'w', 'h', 'thumbnail'}),
    'voice': partial(filter_keys, keys={'url', 'name', 'size', 'duration'}),
}


def main(app_name, fin=sys.stdin, fout=sys.stdout):
    bad_line = False
    domain, type, biz_id, channel, user_type, customer, staff, msg_type, content_ts = [None] * 9
    for line in fin:
        if bad_line:
            content_ts += line
        else:
            domain, type, biz_id, channel, user_type, customer, staff, msg_type, content_ts = line.split(SEP, 8)

        try:
            content, ts = content_ts.rsplit(SEP, 1)
            if not content.endswith('}'):
                raise Exception('bad line')
        except Exception as e:
            if not bad_line:
                bad_line = True
            continue
        bad_line = False

        ts = int(ts)
        if ts > 10000000000:
            ts = float(ts) / 1000
        ts = str(ts)
        content = content.replace('\t', '\\t')
        content = content.replace('\r', '\\r')
        content = content.replace('\n', '\\n')
        content = content.replace('\x0b', '\\u000b')
        content = content.replace('\xa0', '\\u00a0')
        content = content.replace('\\<', '\\\\<')

        msg_domain = ChannelDomainPacker.pack('', channel)
        filter_func = filter_funcs.get(msg_type, filter_keys)
        try:
            if content.startswith('{{'):
                content = content[1:]
            msg = TypeMsgPacker.pack(msg_type, json.dumps(filter_func(json.loads(content)), ensure_ascii=False))
        except Exception as e:
            print('error content: ', ts, content, e, file=sys.stderr)
            msg = TypeMsgPacker.pack(msg_type, content)
        uid = ''
        if user_type == 'c':
            uid = f'{app_name}:customer:{customer}'
        elif user_type == 's':
            uid = f'{app_name}:staff:{staff}'

        fout.write(SEP.join([app_name, domain, type, biz_id, uid, msg_domain, msg, ts]))
        fout.write('\n')
    fout.flush()
    sys.stderr.flush()


if __name__ == '__main__':
    main('qqxb')
