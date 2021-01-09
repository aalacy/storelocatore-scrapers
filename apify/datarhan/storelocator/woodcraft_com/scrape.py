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

    DOMAIN = "woodcraft.com"
    start_url = "https://www.woodcraft.com/store_locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="stores-by-state__store-link"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@itemprop="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = raw_address[2]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//table[@class="table table--hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Please Wear Mask", "")
            if hours_of_operation
            else "<MISSING>"
        )
        hours_of_operation = (
            hours_of_operation.replace(" Face mask required.", "")
            .replace("\n", "")
            .replace("Face Mask Required", "")
            .replace("Masks Required ", "")
        )
        hours_of_operation = (
            hours_of_operation.replace("Face Masks Strong ", "")
            .replace("Face Mask Require", "")
            .replace("masks required", "")
            .replace("Open to the public", "")
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
