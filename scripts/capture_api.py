"""Capture real curl responses from a running application; no response is synthesized."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import quote

parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
args = parser.parse_args()
base = args.base_url.rstrip('/')
root = Path(__file__).resolve().parents[1]
username = os.environ.get('CAPSTONE_USERNAME', 'huynguyen736')
password = os.environ['CAPSTONE_PASSWORD']

with tempfile.TemporaryDirectory() as tmp:
    cookies = str(Path(tmp) / 'cookies.txt')
    def run(path, data=None, token=None):
        command = ['curl.exe' if os.name == 'nt' else 'curl', '-sS', '--fail-with-body', '-b', cookies, '-c', cookies]
        if data is not None:
            command += ['-X', 'POST', '-H', 'Content-Type: application/json', '-H', 'X-CSRFToken: '+token, '--data-raw', json.dumps(data)]
        command += [base+path]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f'curl failed for {path}: {result.stdout} {result.stderr}')
        return result.stdout

    session = json.loads(run('/djangoapp/session'))
    login = run('/djangoapp/login', {'userName': username, 'password':password}, session['csrfToken'])
    root.joinpath('loginuser').write_text(
        '# Actual curl execution against '+base+'\n'
        '# CAPSTONE_PASSWORD is a private environment variable; cookie jar is not submitted.\n'
        'curl -sS -b cookies.txt -c cookies.txt '+base+'/djangoapp/session\n'
        '# Set CSRF_TOKEN from session.csrfToken, then:\n'
        'curl -sS -X POST -b cookies.txt -c cookies.txt -H "Content-Type: application/json" '
        '-H "X-CSRFToken: $CSRF_TOKEN" --data "{\\"userName\\":\\"'+username+'\\",\\"password\\":\\"$CAPSTONE_PASSWORD\\"}" '
        +base+'/djangoapp/login\n\n'+login+'\n', encoding='utf-8')
    session = json.loads(run('/djangoapp/session'))
    logout = run('/djangoapp/logout/', {}, session['csrfToken'])
    root.joinpath('logoutuser').write_text('curl -sS -X POST -b cookies.txt -c cookies.txt -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF_TOKEN" --data "{}" '+base+'/djangoapp/logout/\n\n'+logout+'\n',encoding='utf-8')
    endpoints = {
        'getdealerreviews':'/djangoapp/reviews/dealer/17',
        'getalldealers':'/djangoapp/get_dealers/',
        'getdealerbyid':'/djangoapp/dealer/1',
        'getdealersbyState':'/djangoapp/get_dealers/Kansas',
        'getallcarmakes':'/djangoapp/get_cars',
        'analyzereview':'/djangoapp/analyze/'+quote('Fantastic services'),
    }
    for name,path in endpoints.items():
        output=run(path)
        root.joinpath(name).write_text('curl -sS "'+base+path+'"\n\n'+json.dumps(json.loads(output),indent=2)+'\n',encoding='utf-8')
        print(f'Captured {name}: actual HTTP response')
print('Captured login/logout and six read API artifacts.')
