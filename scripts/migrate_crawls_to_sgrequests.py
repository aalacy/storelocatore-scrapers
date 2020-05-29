import os

def replace_files(base_path):
    os.remove('{}/scrape.py'.format(base_path))
    os.remove('{}/requirements.txt'.format(base_path))
    os.rename('{}/scrape-tmp.py'.format(base_path), '{}/scrape.py'.format(base_path))
    os.rename('{}/requirements-tmp.txt'.format(base_path), '{}/requirements.txt'.format(base_path))

def process_requirements_file(base_path):
    with open('{}/requirements.txt'.format(base_path)) as oldreqs:
        with open('{}/requirements-tmp.txt'.format(base_path), 'w') as newreqs:
            content = oldreqs.readlines()
            for line in content:
                if line.startswith('requests==') or line.strip() == 'requests':
                    newreqs.write('sgrequests\n')
                else:
                    newreqs.write(line)

def process_session_scraper(base_path):
    with open('{}/scrape.py'.format(base_path)) as oldfile:
        with open('{}/scrape-tmp.py'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            for line in content:
                if 'import requests' in line:
                    newfile.write('from sgrequests import SgRequests\n')
                elif 'session = requests.Session' in line:
                    newfile.write('session = SgRequests()\n')
                elif 'requests.get' in line:
                    newfile.write(line.replace('requests.get', 'session.get'))
                elif 'requests.post' in line:
                    newfile.write(line.replace('requests.post', 'session.post'))
                else:
                    newfile.write(line)
    process_requirements_file(base_path)
    replace_files(base_path)

def process_requests_scraper(base_path):
    with open('{}/scrape.py'.format(base_path)) as oldfile:
        with open('{}/scrape-tmp.py'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            import_section = True
            for line in content:
                if 'import requests' in line:
                    newfile.write('from sgrequests import SgRequests\n')
                elif line.strip() and (not line.strip().startswith('#')) and 'import' not in line and import_section:
                    import_section = False
                    newfile.write('\n')
                    newfile.write('session = SgRequests()\n')
                    newfile.write('\n')
                    newfile.write(line)
                elif 'requests.get' in line:
                    newfile.write(line.replace('requests.get', 'session.get'))
                elif 'requests.post' in line:
                    newfile.write(line.replace('requests.post', 'session.post'))
                else:
                    newfile.write(line)
    process_requirements_file(base_path)
    replace_files(base_path)

def process(base_path):
    (_, _, files) = next(os.walk(base_path))
    if 'scrape.py' not in files or 'requirements.txt' not in files:
        print('skipping {}'.format(base_path))
        return
    with open('{}/scrape.py'.format(base_path)) as f:
        content = f.readlines()
        for line in content:
            if 'session = requests.Session' in line:
                process_session_scraper(base_path)
                return
            elif 'requests.get' in line or 'requests.post' in line:
                process_requests_scraper(base_path)
                return

def run(root):
    (_, dirs, _) = next(os.walk(root))
    for dir in dirs:
        process('{}/{}'.format(root, dir))

run('/Users/tenzing/code/crawl-service/apify/himanshu/storelocator')
