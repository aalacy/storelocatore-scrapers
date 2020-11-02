import os

def replace_files(base_path):
    os.remove('{}/scrape.py'.format(base_path))
    os.rename('{}/scrape-tmp.py'.format(base_path), '{}/scrape.py'.format(base_path))

def remove_excess_lines(base_path):
    with open('{}/scrape.py'.format(base_path)) as oldfile:
        with open('{}/scrape-tmp.py'.format(base_path), 'w') as newfile:
            content = oldfile.readlines()
            in_get_driver_method = False
            count = 0
            for line in content:
                if not line.strip():
                    count += 1
                    if count < 2:
                        newfile.write(line)
                else:
                    count = 0
                    newfile.write(line)
    replace_files(base_path)

def process(base_path):
    (_, _, files) = next(os.walk(base_path))
    if 'scrape.py' not in files:
        print('skipping {}'.format(base_path))
        return
    with open('{}/scrape.py'.format(base_path)) as f:
        remove_excess_lines(base_path)

def run(root):
    if root.endswith('storelocator'):
        (_, dirs, _) = next(os.walk(root))
        for dir in dirs:
            process('{}/{}'.format(root, dir))
    else:
        process(root)

run('/Users/tenzing/code/crawl-service/apify/aleenah/storelocator')
