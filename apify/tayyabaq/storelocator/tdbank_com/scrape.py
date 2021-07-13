import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
        for rows in data:
            writer.writerows(rows)


def identify(location):
    return location["profile"]["meta"]["id"]


start_url = "https://locations.td.com/index.html?q={},{}&qp=&locType=stores&l=en"
hdr = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}


@retry(stop=stop_after_attempt(3))
def fetch_locations(coord, tracker, session):
    lat, lng = coord
    response = session.get(start_url.format(lat, lng), headers=hdr)
    data = json.loads(response.text)
    locations = data["response"]["entities"]

    new = []
    for location in locations:
        identity = identify(location)
        if identity not in tracker:
            new.append(extract(location, session))
            tracker.append(identity)

    return new


def get_hours(url, session):
    loc_response = session.get(url)
    loc_dom = etree.HTML(loc_response.text)

    hoo = loc_dom.xpath(
        '//div[@class="c-hours-details-wrapper js-hours-table"]//text()'
    )[1:]
    hoo = [e.strip() for e in hoo if e.strip()]
    return " ".join(hoo).split("{")[0].strip() if hoo else "<MISSING>"


def extract(poi, session):
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    store_url = urljoin(start_url, poi["url"])
    location_name = poi["profile"]["name"]
    location_name = location_name if location_name else "<MISSING>"
    street_address = poi["profile"]["address"]["line1"]
    if poi["profile"]["address"]["line2"]:
        street_address += " " + poi["profile"]["address"]["line2"]
    if poi["profile"]["address"]["line3"]:
        street_address += " " + poi["profile"]["address"]["line3"]
    street_address = street_address if street_address else "<MISSING>"
    city = poi["profile"]["address"]["city"]
    city = city if city else "<MISSING>"
    state = poi["profile"]["address"]["region"]
    state = state if state else "<MISSING>"
    zip_code = poi["profile"]["address"]["postalCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["profile"]["address"]["countryCode"]
    country_code = country_code if country_code else "<MISSING>"
    store_number = poi["profile"].get("c_basicStoreID")
    store_number = store_number if store_number else "<MISSING>"
    phone = poi["profile"]["mainPhone"]["display"]
    phone = phone if phone else "<MISSING>"
    location_type = "<MISSING>"

    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if poi["profile"].get("geocodedCoordinate"):
        latitude = poi["profile"]["geocodedCoordinate"]["lat"]
        longitude = poi["profile"]["geocodedCoordinate"]["long"]

    hours_of_operation = get_hours(store_url, session)

    return [
        domain,
        store_url,
        location_name,
        street_address,
        city,
        state,
        zip_code,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]


def fetch_data():
    # Your scraper here
    scraped_items = []
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    search = static_coordinate_list(5, country_code=SearchableCountries.USA)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_locations, coord, scraped_items, session)
            for coord in search
        ]
        for future in as_completed(futures):
            pois = future.result()
            yield pois


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
