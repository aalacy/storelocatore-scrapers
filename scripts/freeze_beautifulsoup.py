import os

def replace_files(base_path):
    os.remove('{}/requirements.txt'.format(base_path))
    os.rename('{}/requirements-tmp.txt'.format(base_path), '{}/requirements.txt'.format(base_path))

def freeze_beautifulsoup(base_path):
    with open('{}/requirements.txt'.format(base_path)) as oldfile:
        with open('{}/requirements-tmp.txt'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            for line in content:
                if 'bs4' in line:
                    newfile.write('beautifulsoup4==4.8.0\n')
                else:
                    newfile.write(line)
    replace_files(base_path)

def process(base_path):
    (_, _, files) = next(os.walk(base_path))
    if 'requirements.txt' not in files:
        print('skipping {}'.format(base_path))
        return
    freeze_beautifulsoup(base_path)

def run(root):
    if root.endswith('storelocator'):
        (_, dirs, _) = next(os.walk(root))
        for dir in dirs:
            process('{}/{}'.format(root, dir))
    else:
        process(root)

run('/Users/tenzing/code/crawl-service/apify/aleenah/storelocator')
