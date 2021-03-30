import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://row.jimmychoo.com/en/store-locator"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    hdr = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://row.jimmychoo.com",
        "referer": "https://row.jimmychoo.com/en/store-locator",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    countries = {"United Kingdom": "GB", "Canada": "CA", "United States": "US"}
    for country, country_code in countries.items():
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        post_url = dom.xpath('//form[@id="dwfrm_storelocator"]/@action')[0]
        post_url += "&dwfrm_storelocator_findbycountry=ok"
        formdata = {"address": country, "format": "ajax", "country": country_code}
        response = session.post(post_url, data=formdata, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[contains(@href, "store-details")]/@href')

        for url in list(set(all_locations)):
            store_url = urljoin(start_url, url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath("//div/@data-marker-info")[0]
            poi = json.loads(poi)

            location_name = poi["title"]
            location_name = location_name if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//div[@class="js-store-address"]//text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            if "mall " in raw_address[0].lower():
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
            if "Bloomingdale" in raw_address[0]:
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
            if "The Galleria" in raw_address[0]:
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
            if "Fashion Square" in raw_address[0]:
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
            addr = parse_address_intl(" ".join(raw_address))
            addr_poi = parse_address_intl(poi["address"])
            street_address = raw_address[0]
            city = addr.city
            if not city:
                city = addr_poi.city
            if not city and "Chicago" in street_address:
                city = "Chicago"
            if not city and "AVENTURA" in location_name:
                city = "Aventura"
            if not city and "SAN MARCOS" in location_name:
                city = "San Marcos"
            if city.lower() in street_address.lower():
                street_address = " ".join(street_address.split()[:-1])
            state = addr.state
            if not state:
                state = addr_poi.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            if not zip_code:
                zip_code = addr_poi.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            store_number = poi["id"]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = loc_dom.xpath('//div[@class="store-hours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

            item = [
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

            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
