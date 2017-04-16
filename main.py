'''
    Fetch hosts from github.com/racaljk/hosts and replace the system hosts.
'''
import platform
import os
import re
from datetime import datetime
import requests

FETCH_URL = 'https://raw.githubusercontent.com/racaljk/hosts/master/hosts'
MATCH_PATTERN = re.compile(
    r'(.*?# Last updated: )(\d+)-(\d+)-(\d+)(.*?# Modified hosts start)' +
    r'(.*)(# Modified hosts end.*)',
    re.DOTALL | re.S,
)
DATE_FORMAT = '%Y-%m-%d'

def format_date(d):
    return d.strftime(DATE_FORMAT)

def fetch_hosts():
    r = requests.get(FETCH_URL)
    r.raise_for_status()
    return r.text

def match_hosts(content):
    m = MATCH_PATTERN.match(content)
    if m is None:
        return None
    else:
        beg, y, m, d, mid, inner, end = m.groups()
        return datetime(*map(int, [y, m, d])), (beg, mid, end), inner

if platform.system() == 'Windows':
    HOSTS_PATH = os.path.join(os.getenv('SYSTEMROOT'), 'system32', 'drivers', 'etc', 'hosts')
else:
    HOSTS_PATH = '/etc/hosts'

def main():
    with open(HOSTS_PATH, 'r+') as f:
        old_match = match_hosts(f.read())
        new_content = fetch_hosts()
        if old_match is None:
            f.seek(0, 2)
            f.write(new_content)
            print('Append hosts')
        else:
            old_date, (old_beg, old_mid, old_end), _ = old_match
            new_date, _, new_inner = match_hosts(new_content)
            if new_date <= old_date:
                print('Already up to date', format_date(old_date))
            else:
                f.seek(0)
                f.write(''.join([
                    old_beg,
                    format_date(new_date),
                    old_mid,
                    new_inner,
                    old_end
                ]))
                print('Updated from', format_date(old_date), 'to', format_date(new_date))

if __name__ == '__main__':
    main()
