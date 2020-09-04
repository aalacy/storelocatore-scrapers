import os
from shutil import copyfile
import subprocess

def replace_files(base_path):
    os.remove('{}/scrape.py'.format(base_path))
    os.remove('{}/Dockerfile'.format(base_path))
    copyfile('{}/../../../../templates/python3_simple/Dockerfile'.format(base_path), '{}/Dockerfile'.format(base_path))
    os.rename('{}/scrape-tmp.py'.format(base_path), '{}/scrape.py'.format(base_path))

def get_padding(line):
    tab_count, space_count = 0, 0
    for c in line:
        if c == '\t':
            tab_count += 1
        elif c == ' ':
            space_count += 1
        else:
            return '\t'*tab_count + ' '*space_count

def run2to3(base_path):
    subprocess.run(["2to3", "-wn", '{}/scrape-tmp.py'.format(base_path)])

def process_internal(base_path):
    with open('{}/scrape.py'.format(base_path)) as oldfile:
        with open('{}/scrape-tmp.py'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            has_iter_lines = any(['iter_lines()' in x for x in content])
            for line in content:
                if ".encode('utf-8')" in line or '.encode("utf-8")' in line:
                    newfile.write(line.replace(".encode('utf-8')", "").replace('.encode("utf-8")', ""))
                elif ('r = session.' in line or 'r1 = session.' in line or 'r2 = session.' in line or 'r4 = session.' in line) and has_iter_lines:
                    newfile.write(line)
                    newfile.write(get_padding(line) + "if r.encoding is None: r.encoding = 'utf-8'\n")
                elif 'iter_lines()' in line:
                    newfile.write(line.replace('iter_lines()', 'iter_lines(decode_unicode=True)'))
                else:
                    newfile.write(line)
    run2to3(base_path)
    replace_files(base_path)

def process(base_path):
    (_, _, files) = next(os.walk(base_path))
    if 'scrape.py' not in files or 'Dockerfile' not in files:
        print('skipping {}'.format(base_path))
        return
    with open('{}/Dockerfile'.format(base_path)) as f:
        content = f.readlines()
        for line in content:
            if 'apify-python:latest' in line:
                process_internal(base_path)

def run(root):
    if root.endswith('storelocator'):
        (_, dirs, _) = next(os.walk(root))
        for dir in dirs[0:100]:
            print("processing {}".format(dir))
            process('{}/{}'.format(root, dir))
    else:
        print("processing {}".format(root))
        process(root)

run('/Users/tenzing/code/crawl-service/apify/nsxdarin/storelocator')
