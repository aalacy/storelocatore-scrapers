import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    DOMAIN = "compren.com"
    start_url = "http://compren.com/storefind.php"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }
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

    all_locations = []
    for state in states:
        formdata = {"state": state.lower()}
        response = session.post(start_url, data=formdata, headers=headers)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//store")

    for poi_html in all_locations:
        store_url = poi_html.xpath("website_link/text()")
        store_url = store_url[0] if store_url else "<MISSING>"
        loc_name_1 = poi_html.xpath("name/text()")
        if not loc_name_1:
            continue
        loc_name_1 = loc_name_1[0]
        loc_name_2 = poi_html.xpath("store_number/text()")[0]
        location_name = f"Friendly Computers #{loc_name_1} - {loc_name_2}"
        street_address = poi_html.xpath("address/text()")[0]
        structured_result = parse_address_usa(street_address)
        street_address = structured_result.street_address_1
        city = structured_result.city
        if not city:
            city = loc_name_1
            if street_address:
                street_address = street_address.replace(city.lower(), "").strip()
        street_address = street_address if street_address else "<MISSING>"
        city = city if city else "<MISSING>"
        state = poi_html.xpath("state/text()")
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath("zipcode/text()")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = structured_result.country
        store_number = loc_name_2
        phone = poi_html.xpath("phone/text()")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
