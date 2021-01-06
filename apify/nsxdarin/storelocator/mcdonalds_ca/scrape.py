import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mcdonald.ca")
MISSING = "<MISSING>"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Referer": "https://www.mcdonalds.com/us/en-us/restaurant-locator.html",
}


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


def fetch_data(retry_count=0):
    features = []
    try:
        url = "https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do"
        params = {
            "method": "searchLocation",
            "latitude": 43.6424036,
            "longitude": -79.3859716,
            "radius": 15000,
            "maxResults": 50000,
            "country": "ca",
            "language": "en-ca",
            "showClosed": "",
            "hours24Text": "Open 24 hr",
        }
        session = SgRequests().requests_retry_session(retries=0)
        geojson = session.get(url, params=params, headers=headers).json()
        features = geojson["features"]

    except Exception as e:
        logger.error(e)
        if retry_count < 3:
            return fetch_data(retry_count + 1)

    for item in features:
        store = item["properties"]["identifiers"]["storeIdentifier"][0][
            "identifierValue"
        ]
        add = item["properties"]["addressLine1"]
        add = add.strip().replace('"', "'")

        # Special case for head office
        if "This is not a restaurant" in add:
            continue

        city = item["properties"]["addressLine3"]
        state = MISSING
        country = "CA"
        zc = item["properties"]["postcode"]
        try:
            phone = item["properties"]["telephone"]
        except:
            phone = MISSING
        name = "McDonald's # " + store
        website = "mcdonalds.com"
        typ = "Restaurant"
        lat = item["geometry"]["coordinates"][1]
        lng = item["geometry"]["coordinates"][0]
        try:
            hours = "Mon: " + item["properties"]["restauranthours"]["hoursMonday"]
            hours = (
                hours
                + "; Tue: "
                + item["properties"]["restauranthours"]["hoursTuesday"]
            )
            hours = (
                hours
                + "; Wed: "
                + item["properties"]["restauranthours"]["hoursWednesday"]
            )
            hours = (
                hours
                + "; Thu: "
                + item["properties"]["restauranthours"]["hoursThursday"]
            )
            hours = (
                hours + "; Fri: " + item["properties"]["restauranthours"]["hoursFriday"]
            )
            hours = (
                hours
                + "; Sat: "
                + item["properties"]["restauranthours"]["hoursSaturday"]
            )
            hours = (
                hours + "; Sun: " + item["properties"]["restauranthours"]["hoursSunday"]
            )
        except:
            hours = MISSING

        page_url = MISSING
        yield [
            website,
            page_url,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
