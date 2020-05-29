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
                if line.startswith('selenium==') or line.strip() == 'selenium':
                    newreqs.write('sgselenium\n')
                else:
                    newreqs.write(line)

def get_padding(line):
    tab_count, space_count = 0, 0
    for c in line:
        if c == '\t':
            tab_count += 1
        elif c == ' ':
            space_count += 1
        else:
            return '\t'*tab_count + ' '*space_count


def process_get_driver_scraper(base_path):
    with open('{}/scrape.py'.format(base_path)) as oldfile:
        with open('{}/scrape-tmp.py'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            in_get_driver_method = False
            for line in content:
                if 'from selenium import webdriver' in line:
                    newfile.write(get_padding(line) + 'from sgselenium import SgSelenium\n')
                elif 'from selenium.webdriver.chrome.options import Options' in line:
                    continue
                elif 'driver = get_driver()' in line:
                    newfile.write(get_padding(line) + 'driver = SgSelenium().chrome()\n')
                elif 'def get_driver():' in line:
                    in_get_driver_method = True
                    continue
                elif in_get_driver_method and 'return ' in line:
                    in_get_driver_method = False
                    continue
                elif in_get_driver_method:
                    continue
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
        has_get_driver, has_chrome = False, False
        content = f.readlines()
        for line in content:
            if 'driver = get_driver()' in line:
                has_get_driver = True
            elif 'webdriver.Chrome' in line:
                has_chrome = True
        if has_get_driver and has_chrome:
            process_get_driver_scraper(base_path)

def run(root):
    if root.endswith('storelocator'):
        (_, dirs, _) = next(os.walk(root))
        for dir in dirs:
            process('{}/{}'.format(root, dir))
    else:
        process(root)

run('/Users/tenzing/code/crawl-service/apify/ggrahambaker/storelocator')
