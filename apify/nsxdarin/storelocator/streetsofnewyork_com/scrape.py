import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("streetsofnewyork_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def graphql():
    session = SgRequests()
    headers = {
        "Origin": "https://www.streetsofnewyork.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }
    query = {
        "operationName": "restaurantWithLocations",
        "variables": {"restaurantId": 3759},
        "extensions": {"operationId": "PopmenuClient/1314972022f7e2b12673700232e6be54"},
    }
    result = session.post(
        "https://www.streetsofnewyork.com/graphql", json=query, headers=headers
    ).json()
    return result["data"]["restaurant"]["locations"]


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def fetch_data():
    url = "https://www.streetsofnewyork.com/locations"
    locations = graphql()
    for location in locations:
        locator_domain = "streetsofnewyork.com"
        page_url = url
        location_name = get(location, "name")
        store_number = get(location, "id")
        location_type = get(location, "__typename")

        street_address = get(location, "streetAddress")
        city = get(location, "city")
        state = get(location, "state")
        postal = get(location, "postalCode")
        country_code = get(location, "country")
        latitude = get(location, "lat")
        longitude = get(location, "lng")

        phone = get(location, "phone")
        hours_of_operation = ",".join(get(location, "schemaHours"))
        yield [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
