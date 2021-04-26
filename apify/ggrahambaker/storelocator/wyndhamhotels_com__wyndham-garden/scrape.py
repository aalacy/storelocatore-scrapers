from sglogging import SgLogSetup
from sgrequests import SgRequests
from lxml import html
import re
import csv
import json

logger = SgLogSetup().get_logger("wyndhamhotels_com__wyndham-garden")
DOMAIN = "https://www.wyndhamhotels.com"
MISSING = "<MISSING>"


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
        for row in data:
            writer.writerow(row)


def get_store_urls(domobj):
    xpath_us_ca = '//h4[contains(text(), "United States")]/following-sibling::*[count(following-sibling::h4[contains(text(), "Mexico")])=1]'
    url_us_ca_raw = domobj.xpath(xpath_us_ca)
    url_us_ca = []
    for uucr in url_us_ca_raw:
        url_per_state = uucr.xpath("./div/ul/li/a/@href")
        url_us_ca.extend(url_per_state)
    url_us_ca = [uuc for uuc in url_us_ca if "overview" in uuc]
    url_us_ca = [f"{DOMAIN}{url}" for url in url_us_ca]
    return url_us_ca


def fetch_data():
    # Your scraper here

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.wyndhamhotels.com/wyndham-garden/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = html.fromstring(response.text, "lxml")
    url_stores = get_store_urls(dom)
    items = []
    for idx, url_store in enumerate(url_stores):
        page_url = url_store
        loc_response = session.get(url_store, headers=hdr)
        loc_dom = html.fromstring(loc_response.text, "lxml")
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        logger.info(f"Pulling the data at {idx} out of {len(url_stores)}: {page_url} ")
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            location_name = location_name if location_name else MISSING
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else MISSING
            city = poi["address"]["addressLocality"]
            city = city if city else MISSING
            state = poi["address"].get("addressRegion")
            state = state if state else MISSING
            zip_code = poi["address"].get("postalCode")
            zip_code = zip_code if zip_code else MISSING
            country_code = poi["address"]["addressCountry"]
            country_code = country_code if country_code else MISSING
            if country_code not in ["Canada", "United States"]:
                continue
            store_number = MISSING
            phone = poi["telephone"]
            phone = phone if phone else MISSING
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            location_name = loc_dom.xpath('//span[@class="prop-name"]/text()')
            location_name = location_name[0] if location_name else MISSING
            street_address = re.findall(
                "property_city_name = '(.+?)';", loc_response.text
            )
            street_address = street_address[0] if street_address else MISSING
            city = re.findall("property_city_name = '(.+?)';", loc_response.text)
            city = city[0] if city else MISSING
            state = re.findall("property_state_code = '(.+?)';", loc_response.text)
            state = state[0] if state else MISSING
            zip_code = re.findall("property_postal_code = '(.+?)';", loc_response.text)
            zip_code = zip_code[0] if zip_code else MISSING
            country_code = re.findall(
                "property_country_code = '(.+?)';", loc_response.text
            )
            country_code = country_code[0] if country_code else MISSING
            store_number = MISSING
            phone = [
                e
                for e in loc_dom.xpath(
                    '//nav[@id="mainNav"]//a[contains(@href, "tel")]/text()'
                )
                if "(" in e
            ]
            phone = phone if phone else MISSING
            location_type = MISSING
            latitude = MISSING
            longitude = MISSING

        hours_of_operation = MISSING

        item = [
            domain,
            page_url,
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

        items.append(item)
    return items


def scrape():
    scraping_started = "Scraping Started"
    logger.info(f"{scraping_started}")
    data = fetch_data()
    write_output(data)
    logger.info(f"Total store processed: {len(data)}")


if __name__ == "__main__":
    scrape()
