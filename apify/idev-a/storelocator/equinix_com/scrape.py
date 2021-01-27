import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.equinix.com/data-centers/americas-colocation/'
    r = session.get(locator_domain)
    soup = bs(r.text, 'lxml')
    sections = soup.select('div.eq-region')
    data = []
    import pdb; pdb.set_trace()
    for section in sections:
        if section.h2.id == 'united-states' or section.h2.id == 'canada':
            links = section.select('a')
            for link in links:
                page_url = urljoin('https://www.equinix.com', link['href'])
                r1 = session.get(page_url)
                soup1 = bs(r1.text, 'lxml')
                lead = soup1.select_one('div.eq-ibx-contact p').text
                store_number = myutil._valid(location['id'])
                location_name = location['store']
                street_address = myutil._valid(f"{location.get('address')} {location.get('address2')}")
                city = myutil._valid(location.get('city'))
                state = myutil._valid(location.get('state'))
                zip = myutil._valid(location.get('zip'))
                country_code = myutil.get_country_by_code(state)
                phone = myutil._valid(location.get('phone'))
                location_type = '<MISSING>'
                latitude = myutil._valid(location.get('lat'))
                longitude = myutil._valid(location.get('lng'))
                tags = bs(location['hours'], "lxml")
                hours = []
                for tag in tags.select('tr'):
                    hours.append(f"{tag.td.text}: {tag.select_one('td time').text}")
                hours_of_operation = "; ".join(hours)

                _item = [
                    locator_domain,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]

                myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
