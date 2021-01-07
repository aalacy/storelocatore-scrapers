import csv
from urllib.parse import urljoin
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
    scraped_items = []

    DOMAIN = "winsupplyinc.com"
    start_url = "https://www.woodhousespas.com/spa-locator"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="item-list"]/ul/li')
    next_page = dom.xpath('//a[@title="Go to next page"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="item-list"]/ul/li')
        next_page = dom.xpath('//a[@title="Go to next page"]/@href')

    for poi_html in all_locations:
        url = poi_html.xpath('.//div[@class="button more-information-button"]/a/@href')
        if not url:
            url = poi_html.xpath('.//span[@class="field-content"]/a/@href')
        if not url:
            continue

        store_url = urljoin(start_url, url[0])
        location_name = poi_html.xpath('.//span[@class="red"]/text()')
        location_name = (
            location_name[0].replace(",", "").strip().split("Please")[0]
            if location_name
            else "<MISSING>"
        )
        try:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_address = loc_dom.xpath('//div[@class="location-address"]/text()')
            raw_address = [elem.strip() for elem in raw_address]
            if len(raw_address) == 3:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            street_address = raw_address[0]
            city = raw_address[-1].split(", ")[0]
            state = " ".join(raw_address[-1].split(", ")[-1].split()[:-1])
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//div[contains(@class, "phone-number")]/div/div/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            latitude = latitude if latitude else "<MISSING>"
            longitude = "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//div[contains(@class, "field-hours")]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation).split("Call")[0].split("Please")[0]
                if hours_of_operation
                else "<MISSING>"
            )
        except Exception:
            raw_address = poi_html.xpath('.//div[@class="locationAddress"]/a/text()')
            raw_address = [elem.strip() for elem in raw_address]
            if len(raw_address) == 3:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = " ".join(raw_address[1].split(", ")[-1].split()[:-1])
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//div[@class="locationPhone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            latitude = latitude if latitude else "<MISSING>"
            longitude = "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi_html.xpath(
                './/div[@class="views-field-field-hours"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation).split("Call")[0]
                if hours_of_operation
                else "<MISSING>"
            )

        # Exceptions
        street_address = street_address.replace("Two locations to serve you!, ", "")
        hours_of_operation = (
            "00 pm".join(hours_of_operation.split("00 pm")[:-1]) + "00 pm"
        )
        hours_of_operation = hours_of_operation.split("Closed Thanksgiving")[0]

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
        if street_address not in scraped_items:
            scraped_items.append(street_address)
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
