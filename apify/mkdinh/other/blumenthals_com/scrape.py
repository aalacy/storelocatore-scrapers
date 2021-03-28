import csv
from sglogging import SgLogSetup
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("blumenthals_com")
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

MISSING = "<MISSING>"
FIELDS = [
    "category_tag",
    "places_categories_source",
    "page_url",
    "category_result",
]


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def load_category_tags():
    with open('categories.csv') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        return [row[0] for row in reader]


def load_sources():
    return [
        {'slug': 'en-APL', 'name': 'Apple (APL)'},
        {'slug': 'en-US(PfB)', 'name': 'Google English (US)(PfB)'}
    ]


def get_by_tag_source(tag, source):
    url = 'https://blumenthals.com/google-lbc-categories/search.php'
    params = {
        'q': tag,
        'hl-gl': source,
        'ottype': 1,
        'val': None

    }
    return session.get(url, params=params, headers=headers)


def fetch_categories(tag, source):
    response = get_by_tag_source(tag, source['slug'])
    soup = BeautifulSoup(response.text, 'html.parser')

    categories = []
    nodes = soup.find_all('tr')
    if len(nodes):
        headers, *rows = soup.find_all('tr')

        for row in rows:
            category = row.find('td').getText()
            categories.append(category)

    return {
        'page_url': response.url,
        'category_tag': tag,
        'places_categories_source': source['name'],
        'category_result': ','.join(categories) or MISSING,
    }


def fetch_data():
    tags = load_category_tags()
    sources = load_sources()

    futures = []

    with ThreadPoolExecutor() as executor:
        for source in sources:
            for tag in tags:
                future = executor.submit(fetch_categories, tag, source)
                futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            yield [result[field] for field in FIELDS]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
