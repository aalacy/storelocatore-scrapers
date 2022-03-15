import re
import csv
import json
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

    start_url = "https://knowledgetags.yextpages.net/embed?key=-668exv0m03CTGweOOgstodtcXsQs32vTknFtZZuGe2EDA_CHG4JGlr2oiM1j6wN&account_id=2903957495944679166&entity_id=2691&entity_id=2695&entity_id=2689&entity_id=2685&entity_id=2687&entity_id=2692&entity_id=2693&entity_id=2690&entity_id=7054&locale=en"
    domain = "hornbachers.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall(r"Yext._embed\((.+)", response.text)
    data = re.findall(r"Yext._embed\((.+)", response.text)[0]
    data = json.loads(data)

    response = session.get("https://www.hornbachers.com/NEW/stores")
    dom = etree.HTML(response.text)
    names = dom.xpath('//div[@class="caption"]/h3/text()')

    for i, poi in enumerate(data["entities"]):
        store_url = "https://www.hornbachers.com/NEW/stores"
        location_name = names[i]
        street_address = poi["attributes"]["address.line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["attributes"]["address.city"]
        city = city if city else "<MISSING>"
        state = poi["attributes"]["address.region"]
        state = state if state else "<MISSING>"
        zip_code = poi["attributes"]["address.postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["attributes"]["address.countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["attributes"]["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["schema"]["geo"]["latitude"]
        longitude = poi["schema"]["geo"]["longitude"]
        hoo = []
        for elem in poi["schema"]["openingHoursSpecification"]:
            day = elem["dayOfWeek"]
            opens = elem["opens"]
            closes = elem["closes"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
