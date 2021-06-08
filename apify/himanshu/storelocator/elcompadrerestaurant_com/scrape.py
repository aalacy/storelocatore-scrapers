import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.elcompadrerestaurant.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@id, "divModMaps")]')
    for i, poi_html in enumerate(all_locations):
        mod_id = poi_html.xpath("@data-sitepagemoduleid")[0]
        url = "https://websiteoutputapi.mopro.com/WebsiteOutput.svc/api/get"
        payload = {
            "method": "GetLocation",
            "format": "json",
            "parameters": f"ProjectID=dd705a88-4393-4a30-b8d0-d143f12fa92b&SitePageModuleID={mod_id}",
            "typefields": [{"DataType": "BusObj", "Columns": "*"}],
            "async": False,
            "host": "websiteoutput",
            "params": f"ProjectID=dd705a88-4393-4a30-b8d0-d143f12fa92b&SitePageModuleID={mod_id}",
        }
        poi = session.post(url, json=payload).json()
        poi = poi[1]["rows"][0]

        store_url = start_url
        location_name = poi["Name"]
        street_address = poi["Address"]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        raw_address = poi["City"]
        city = raw_address.split(", ")[0]
        state = raw_address.split(", ")[-1].split()[0]
        zip_code = raw_address.split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[contains(@id, "Phonenum")]/text()')
        phone = phone[0].split("Phone. ")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]

        hoo = dom.xpath(
            '//div[h3[contains(text(), "HOURS OF OPERATION")]]/following-sibling::div//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("(Covid-19 Temporary Hours)")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            hoo[i - 1].split("HOURS:")[-1].split("Last seating")[0].strip()
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
