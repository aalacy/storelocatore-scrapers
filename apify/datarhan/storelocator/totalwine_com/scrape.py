import csv
from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests


from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("totalwine_com")


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


@retry(stop=stop_after_attempt(5))
def get_url(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    session = SgRequests()
    response = session.get(url, headers=headers)
    return response.json()


def fetch_data():
    items = []

    DOMAIN = "totalwine.com"

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

    start_url = "https://www.totalwine.com/store-finder/api/store/storelocator/v1/storesbystate/{}"
    all_locations = []
    for state in states:
        data = get_url(start_url.format(state))
        if not data.get("stores"):
            logger.info(f"no data found for state: {state}")
            continue
        all_locations += data["stores"]

    for poi in all_locations:
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi.get("address1")
        if street_address:
            if poi["address2"]:
                street_address = poi["address2"]
        else:
            street_address = poi.get("address2")
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateShort"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["stateIsoCode"]
        country_code = country_code.split("-")[0] if country_code else "<MISSING>"
        store_number = poi["storeNumber"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["storeHours"]["days"]:
            day = elem["dayOfWeek"]
            opens = elem["openingTime"]
            closes = elem["closingTime"]
            if opens == closes:
                hours_of_operation.append(f"{day} closed")
            else:
                hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        store_url = "https://www.totalwine.com/store-info/{}-{}/{}".format(
            poi["state"].lower(), city.replace(" ", "-"), store_number
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
