import csv
from sgrequests import SgRequests
import json
from sglogging import sglog

website = "restaurantdepot.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    locations_resp = session.get(
        "https://www.restaurantdepot.com/locations/find-a-warehouse"
    )

    loc_list = []
    try:
        locations = json.loads(
            locations_resp.text.split("var model = ")[1]
            .strip()
            .split("</script>")[0]
            .strip()
        )["Locations"]

        for l in locations:
            page_url = "https://www.restaurantdepot.com/locations/find-a-warehouse"
            location_name = l["Title"]
            street_address = l["Address"]["Street"]
            city = l["Address"]["City"]
            state = l["Address"]["StateCode"]
            zip = l["Address"]["Zip"]
            country_code = l["Address"]["CountryCode"]
            store_number = l["Branch"]
            phone = l["Phone"]
            if phone == "":
                phone = "<MISSING>"
            location_type = ", ".join(l["Services"]).strip()
            if location_type == "":
                location_type = "<MISSING>"
            latitude = l["Address"]["Latitude"]
            longitude = l["Address"]["Longitude"]
            hours_of_operation = (
                l["StoreHours"]
                .replace("<div>", "")
                .replace("<p>", "")
                .replace("<span>", "")
                .replace("</span>", "")
                .replace("<br />", "")
                .replace("</p>", "")
                .replace("</div>", "")
                .strip()
                .replace("&nbsp;", " ")
                .strip()
            )
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

            curr_list = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            loc_list.append(curr_list)

    except json.decoder.JSONDecodeError:
        log.error(f"cannot parse json")

    log.info(f"No of records being processed: {len(loc_list)}")

    return loc_list


def scrape():
    data = fetch_data()

    write_output(data)
    log.info(f"Finished")


if __name__ == "__main__":
    scrape()
