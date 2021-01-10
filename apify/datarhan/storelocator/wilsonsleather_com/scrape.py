import re
import json
import csv
from lxml import etree
from sgrequests import SgRequests


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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "wilsonsleather.com"
    start_url = "https://www.wilsonsleather.com/store-locator/all-stores.do"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//div[@class="eslStore ml-storelocator-headertext"]/a/@href')

    for url in all_urls:
        store_url = "https://www.wilsonsleather.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        poi = store_dom.xpath(
            '//script[contains(text(), "storeLocatorDetail")]/text()'
        )[0]
        poi = re.findall("({.+}),", poi.replace("\n", "").replace("\r", ""))[0]
        poi = json.loads(poi)

        location_name = poi["results"][0]["name"]
        street_address = poi["results"][0]["address"]["street1"]
        if poi["results"][0]["address"]["street2"]:
            street_address += ", " + poi["results"][0]["address"]["street2"]
        if poi["results"][0]["address"]["street3"]:
            street_address += ", " + poi["results"][0]["address"]["street3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["results"][0]["address"]["city"]
        state = poi["results"][0]["address"]["stateCode"]
        zip_code = poi["results"][0]["address"]["postalCode"]
        country_code = poi["results"][0]["address"]["countryName"]
        store_number = poi["results"][0]["code"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["results"][0]["address"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["results"][0]["location"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["results"][0]["location"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//span[@class="ml-storelocator-hours-details"]//p/text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = [
            DOMAIN,
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


hdr = {
    "authority": "www.winsupplyinc.com",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
    "content-type": "application/json",
    "cookie": "BIGipServerorigin_prod=303169802.20480.0000; rxVisitor=16071916149854JST89CK49VG5PBOCK7134ILNF7TFJVC; _ga=GA1.2.80294118.1607191617; __auc=c84dd6231763415e7b3c3d1188e; dtSa=-; _gid=GA1.2.1487140172.1607334507; JSESSIONID=TSE8zklXws_EJ1-s-8-S-98D4tMSnndgvYjE2XIU4BpYzOq4L27B!793648615; _gat=1; __asc=57314b9a1763cce50c75056b9da; dtCookie=v_4_srv_3_sn_C36FEEFA25E4840B524DB33205FD55E7_perc_100000_ol_0_mul_1; dtLatC=4; rxvt=1607339756231|1607336305512; dtPC=3$537927365_149h11vTNMKEAFMCQELCPNSKUMIOCTWARMDFODC-0e3",
    "origin": "https://www.winsupplyinc.com",
    "referer": "https://www.winsupplyinc.com/location-finder",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-dtpc": "3$537927365_149h11vTNMKEAFMCQELCPNSKUMIOCTWARMDFODC-0e3",
}
