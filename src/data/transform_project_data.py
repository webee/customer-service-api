import sys
import json


def main(fin=sys.stdin, fout=sys.stdout):
    for line in fin:
        proj = json.loads(line)
        del proj['id']
        proj['start_msg_id'] = 300000
        fout.write(json.dumps(proj, ensure_ascii=False))
        fout.write('\n')
    fout.flush()


if __name__ == '__main__':
    main()
