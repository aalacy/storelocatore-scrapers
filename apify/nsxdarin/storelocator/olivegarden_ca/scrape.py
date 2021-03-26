from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgselenium import SgChrome
from lxml import html
import json
import time
import csv

logger = SgLogSetup().get_logger("olivegarden_ca")
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    urls = []
    items = []
    url = "https://www.olivegarden.ca/ca-locations-sitemap.xml"
    r = session.get(url, headers=headers)

    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>" in line:
            urls.append(line.split("<loc>")[1].split("<")[0])

    for url_store in urls:
        with SgChrome() as driver:
            driver.get(url_store)
            time.sleep(60)
            location_raw_data = driver.page_source

        locator_domain_name = "olivegarden.ca"
        tree = html.fromstring(location_raw_data)
        json_raw_data = tree.xpath('//script[@type="application/ld+json"]/text()')
        json_clean = "".join(json_raw_data).replace("\n", "")
        logger.info(("\nParsing data from.... \n%s\n" % json_clean))
        json_data = json.loads(json_clean)
        page_url = json_data["url"] or "<MISSING>"
        locator_domain = locator_domain_name
        location_name = json_data["name"] or "<MISSING>"
        street_address = json_data["address"]["streetAddress"].strip() or "<MISSING>"
        city = json_data["address"]["addressLocality"].strip() or "<MISSING>"
        state = json_data["address"]["addressRegion"].strip() or "<MISSING>"
        country_code = json_data["address"]["addressCountry"] or "<MISSING>"
        zip = json_data["address"]["postalCode"].strip() or "<MISSING>"
        store_number = json_data["branchCode"] or "<MISSING>"
        phone = json_data["telephone"].strip() or "<MISSING>"
        location_type = json_data["@type"] or "<MISSING>"
        latitude = json_data["geo"]["latitude"] or "<MISSING>"
        longitude = json_data["geo"]["longitude"] or "<MISSING>"
        hoo = json_data["openingHours"]
        if hoo:
            hoo = "; ".join(hoo)
            hours_of_operation = hoo
        else:
            hours_of_operation = "<MISSING>"
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
