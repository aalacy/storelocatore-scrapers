import csv
from lxml import html
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('picturehouses_com')


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


session = SgRequests()


def get_urls():

    locator_domain = "https://www.chronictacos.com"
    us_locations_url = "https://www.chronictacos.com/us-locations"
    ca_locations_url = "https://www.chronictacos.com/canada-locations"
    jp_locations_url = "https://www.chronictacos.com/japan-locations"
    list_of_countries_urls = [us_locations_url, ca_locations_url, jp_locations_url]
    all_location_urls = []
    for url in list_of_countries_urls:
        if "us" in url:
            us_r = session.get(url)
            us_tree = html.fromstring(us_r.text)
            us_location_detail_url = us_tree.xpath('//h3[contains(@class, "l-location")]/a/@href')
            for url_location in us_location_detail_url:
                all_location_urls.append(url_location)
        elif "canada" in url:
            ca_r = session.get(url)
            ca_tree = html.fromstring(ca_r.text)
            ca_location_detail_url = ca_tree.xpath('//section[contains(@class, "menu-section")]//a/@href')
            for url_location in ca_location_detail_url:
                full_url = locator_domain + "/" + url_location
                all_location_urls.append(full_url)

        elif "japan" in url:
            jp_r = session.get(url)
            jp_tree = html.fromstring(jp_r.text)
            jp_location_detail_url = jp_tree.xpath('//section[contains(@class, "menu-section")]//li[1]/a/@href')
            for url_location in jp_location_detail_url:
                full_url = locator_domain + "/" + url_location
                all_location_urls.append(full_url)
        else:
            all_location_urls = ''
    return all_location_urls


def fetch_data():

    # Your scraper here
    locator_domain = "https://www.chronictacos.com"
    urls = get_urls()
    items = []
    for url_location in urls:
        r_location = session.get(url_location)
        tree_obj = html.fromstring(r_location.text)
        json_raw_data = tree_obj.xpath('//script[@type="application/ld+json"]/text()')
        json_raw_data = json_raw_data[1]
        json_data = json.loads(json_raw_data, strict=False)
        locator_domain = locator_domain
        page_url = json_data['url']
        location_name = json_data['name']
        street_address_data = json_data['address']['streetAddress'].strip()
        if street_address_data:
            street_address = street_address_data
        else:
            street_address = "<MISSING>"

        city_data = json_data['address']['addressLocality'].strip()
        if city_data:
            city = city_data
        else:
            city = "<MISSING>"
        state_data = json_data['address']['addressRegion'].strip()

        if state_data:
            state = state_data
        else:
            state = "<MISSING>"

        country_code_data = json_data['address']['addressCountry']
        if country_code_data:
            country_code = country_code_data.strip()
        else:
            country_code = "<MISSING>"

        zip_data = json_data['address']['postalCode'].strip()
        if zip_data:
            zip = zip_data
        else:
            zip = "<MISSING>"

        store_number = '<MISSING>'
        phone_data = json_data['telephone']
        if phone_data:
            phone = phone_data
        else:
            phone = "<MISSING>"

        location_type = json_data['@type']
        latitude = json_data['geo']['latitude']
        longitude = json_data['geo']['longitude']

        hoo = json_data['openingHours']
        hoo1 = [i.strip() for i in hoo.split('\n')]
        hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
        hoo3 = "; ".join(hoo2)
        if hoo3:
            hoo1 = [i.strip() for i in hoo.split('\n')]
            hoo2 = [" ".join(i.strip().split()) for i in hoo1 if i]
            hoo3 = "; ".join(hoo2)
            hours_of_operation = hoo3
        else:
            hours_of_operation = '<MISSING>'

        row = [
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
        items.append(row)
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
