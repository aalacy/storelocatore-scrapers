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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "belk.com"
    start_url = "https://www.belk.com/stores-near-you/"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    for code in states:
        body = "dwfrm_storelocator_postalCode=&dwfrm_storelocator_state={}".format(code)
        response = session.post(start_url, data=body, headers=headers)
        data = json.loads(response.text)
        for poi in data["stores"]:
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["stateCode"]
            state = state if state else "<MISSING>"
            zip_code = poi["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"

            store_url = "https://www.belk.com/store/{}-{}/?StoreID={}".format(
                city, state, store_number
            )
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)
            store_data = store_dom.xpath('.//div[@id="primary"]/script/text()')[0]
            store_data = json.loads(store_data.replace("\n", "").replace(",},", "},"))
            location_type = store_data["@type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = store_data["geo"]["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = store_data["geo"]["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = store_dom.xpath(
                '//dl[@class="store-hours-list"]//text()'
            )
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
