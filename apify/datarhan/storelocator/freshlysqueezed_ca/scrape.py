import re
import csv
from lxml import etree

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

    start_url = "http://www.freshlysqueezed.ca/stores/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    all_ids = re.findall(r"cspm_new_pin_object\(.+'(\d+)',", response.text)
    post_url = "http://www.freshlysqueezed.ca/dev/wp-admin/admin-ajax.php"
    hdr = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    for store_number in all_ids:
        formdata = {
            "action": "cspm_load_carousel_item",
            "post_id": store_number,
            "items_view": "listview",
        }
        loc_response = session.post(post_url, data=formdata, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        store_url = start_url
        location_name = loc_dom.xpath("//a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = " ".join(loc_dom.xpath('//div[@class="details_infos"]/text()'))
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        if "…" in street_address:
            street_address = "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        if not state and "," in raw_address:
            state = raw_address.split(",")[-1].split()[0]
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code and "," in raw_address:
            zip_code = " ".join(raw_address.split(",")[-1].split()[1:])
        zip_code = zip_code.replace("…", "") if zip_code else "<MISSING>"
        country_code = "CA"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall("{}', (.+?), '', map_id".format(store_number), response.text)[
            0
        ].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = "<MISSING>"

        if "NOVA" in zip_code:
            zip_code = "<MISSING>"
        if "UNIT" in zip_code:
            zip_code = "<MISSING>"
        if "Unit" in zip_code:
            zip_code = zip_code.replace("Unit", "").strip()
        zip_code = zip_code if zip_code else "<MISSING>"

        if state == "HALIFAX":
            state = "<MISSING>"

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
