import nfc
from nfc.clf import LocalTarget, TimeoutError, BrokenLinkError
import argparse
import json
fromhex = bytearray.fromhex

parser = argparse.ArgumentParser(
    description='Replay felica exchange', epilog='v1.1')

parser.add_argument('FILE', help='Replay File')
parser.add_argument('-d', '--device', help='Device')
parser.add_argument('-t', '--timeout', help='timeout',
                    type=float, default=0.005)

args = parser.parse_args()

FILE = args.FILE
DEVICE = 'usb'
if args.device:
    DEVICE = args.device
TIMEOUT = args.timeout

print('TIMEOUT', TIMEOUT, 's')

qa = {}

for l in open(FILE, 'r'):
    l = l.replace('\n', '')
    d = l[3:]
    if l.startswith('<>'):
        print('<>', d)
        card = json.loads(d)
        if card['idm'].lower() == 'random':  # TODO
            pass
    if l.startswith('<<'):
        q = d.lower()
    if l.startswith('>>'):
        a = d.lower()
        qa[q] = a

sensf_res = fromhex('01'+card['idm']+card['pmm']+card['sys'])

clf = nfc.ContactlessFrontend(DEVICE)
target = clf.listen(LocalTarget(
    "212F", sensf_res=sensf_res), timeout=60.)

if target is None:
    print('No Reader')
    exit(-1)

tt3_cmd = target.tt3_cmd
rsp = (len(tt3_cmd) + 1).to_bytes(1, "big") + tt3_cmd

while True:
    print('<<', rsp.hex())
    try:
        com = fromhex(qa[rsp.hex()])
        print('>>', com.hex())
    except KeyError:
        print('Unknown Command')
        com = None
    try:
        rsp = clf.exchange(com, TIMEOUT)
    except TimeoutError:
        print('TIMEOUT Reader')
        break
    except BrokenLinkError:
        print('Exchange Finished')
        break

clf.close()
