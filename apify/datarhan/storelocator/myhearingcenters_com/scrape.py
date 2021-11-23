import re
import csv
from lxml import etree
from urllib.parse import urljoin

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://myhearingcenters.com/wp-admin/admin-ajax.php?action=store_search&lat=40.56498&lng=-111.83897&max_results=100&search_radius=100&autoload=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        store_url = urljoin("https://myhearingcenters.com/", poi["url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["store"]
        location_name = (
            location_name.replace("&#8211;", "-") if location_name else "<MISSING>"
        )
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//li[i[@class="x-icon-clock-o"]]//text()')
        hoo = [
            e.replace("Please call us for our hours", "")
            .replace("Call for Hours", "")
            .strip()
            for e in hoo
            if e.strip()
        ]
        hoo = (
            " ".join(hoo)
            .replace("Hours: By appointment only", "")
            .replace("Mon, Thurs, Fri: N/A", "")
            .replace("Please call us for hours.", "")
            .replace("By appointment only", "")
        )
        hours_of_operation = (
            hoo.replace("pmFridays", "pm Fridays") if hoo else "<MISSING>"
        )

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
