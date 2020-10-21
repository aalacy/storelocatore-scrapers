import csv

from sgselenium import SgChrome
from bs4 import BeautifulSoup
from sgscrape import simple_utils as sg_utils
from sglogging import SgLogSetup

DOMAIN = 'https://www.tillys.com'
logger = SgLogSetup().get_logger('tillys.com')

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(sg_utils.sorted_keys(sg_utils.sg_record()))
        # Body
        counter = 0
        for row in data:
            counter += 1
            writer.writerow(sg_utils.sort_values_dict(row))

        logger.debug(f'Wrote {counter} records to file.')

def parse_lat_long(google_maps_link: str) -> (str, str):
    arr = google_maps_link.split('/')[-1].split(',')
    return arr[0], arr[1]

def fetch_data():
    with SgChrome() as driver:
        driver.set_page_load_timeout(120)
        driver.rewrite_rules = [
            (r'^((?!tillys.com/store-list).)*$', r'about:blank') # disregard all requests that aren't this page
        ]
        driver.get("https://www.tillys.com/store-list")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        locations = soup.find_all('div', {'class': 'sl__stores-list_item'})
        for loc in locations:
            try:
                links = loc.find_all('a')
                about_link = [l for l in links if l.get('class') and 'sl__stores-list_name-link' in l['class']][0]
                location_name = about_link['title']

                if 'Coming Soon!' in location_name:
                    continue # not an operating store yet; missing several fields

                directions_link = [l for l in links if l.get('aria-label') and 'Driving directions to store' in l['aria-label']][0]
                telephone_links =  [l for l in links if 'tel:' in l['href']]
                telephone = telephone_links[0].text if telephone_links else sg_utils.MISSING

                lat, long = parse_lat_long(directions_link['href'])

                locality = [x for x in loc.find('div', {'itemprop': 'addressLocality'}).text.replace('\n', ',').split(',') if x]

                hours_raw = [i for i in loc.find('time').text.split('\n') if i]
                hours = ', '.join([f'{day}: {time}' for day, time in zip(hours_raw[:7],hours_raw[7:])])

                rec = sg_utils.sg_record(
                    page_url=f"{DOMAIN}{about_link['href']}",
                    locator_domain=DOMAIN,
                    latitude=lat,
                    longitude=long,
                    store_number= loc.find('span', {'itemprop':'branchCode'}).text,
                    location_name=location_name,
                    street_address=loc.find('div', {'itemprop':'streetAddress'}).text.replace('\n',' ').strip(),
                    state=locality[-2],
                    country_code='us', # only US locations at the moment of writing
                    city=", ".join(locality[:-2]),
                    zip_postal=locality[-1],
                    phone=sg_utils.or_missing(lambda: telephone),
                    hours_of_operation=sg_utils.or_missing(lambda: hours))
                yield rec

            except BaseException as e:
                logger.error(loc, exc_info=e)
                raise e

def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == '__main__':
    scrape()
