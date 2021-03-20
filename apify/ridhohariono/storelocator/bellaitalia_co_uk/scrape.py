import csv
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "bellaitalia.co.uk"
BASE_URL = "https://www.bellaitalia.co.uk"
API_STORES = "https://api.bigtablegroup.com/pagedata/?brandKey=bellaitalia&path=/spaces/com0r9vws8o2/entries?access_token=f99c643342fea1841fda74418f0263d3af7b096dc78413cb9747c6bf5221beaf%26select=fields.storeId,fields.title,fields.slug,fields.city,fields.description,fields.addressLocation,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.phoneNumber,fields.email,fields.hours,fields.alternativeHours%26content_type=restaurant%26include=1"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    log.info("Write Output of " + DOMAIN)
    with open("data.csv", mode="w") as output_file:
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def get_hours(id, includes):
    hoo = []
    for row in includes["Entry"]:
        if row["sys"]["id"] == id:
            hoo.append(
                [
                    "monday: "
                    + row["fields"]["mondayOpen"]
                    + " - "
                    + row["fields"]["mondayClose"],
                    "tuesday: "
                    + row["fields"]["tuesdayOpen"]
                    + " - "
                    + row["fields"]["tuesdayClose"],
                    "wednesday: "
                    + row["fields"]["wednesdayOpen"]
                    + " - "
                    + row["fields"]["wednesdayClose"],
                    "thursday: "
                    + row["fields"]["thursdayOpen"]
                    + " - "
                    + row["fields"]["thursdayClose"],
                    "friday: "
                    + row["fields"]["fridayOpen"]
                    + " - "
                    + row["fields"]["fridayClose"],
                    "saturday: "
                    + row["fields"]["saturdayOpen"]
                    + " - "
                    + row["fields"]["saturdayClose"],
                    "sunday: "
                    + row["fields"]["sundayOpen"]
                    + " - "
                    + row["fields"]["sundayClose"],
                ]
            )
    return "<MISSING>" if not hoo else ", ".join(hoo[0])


def fetch_data():
    log.info("Fetching store_locator data")
    store_details = session.get(API_STORES, headers=HEADERS).json()
    locations = []
    for row in store_details["items"]:
        locator_domain = DOMAIN
        page_url = BASE_URL
        location_name = row["fields"]["title"]
        if "addressLine2" in row["fields"] and len(row["fields"]["addressLine2"]) > 0:
            street_address = "{}, {}".format(
                row["fields"]["addressLine1"], row["fields"]["addressLine2"]
            )
        else:
            street_address = row["fields"]["addressLine1"]
        city = handle_missing(row["fields"]["city"])
        state = handle_missing(row["fields"]["county"])
        zip_code = handle_missing(row["fields"]["postCode"])
        country_code = "GB"
        store_number = row["fields"]["storeId"]
        phone = handle_missing(row["fields"]["phoneNumber"])
        if "We're temporarily closed" in row["fields"]["description"]:
            location_type = "TEMP_CLOSED"
        elif "We're open for Delivery & Collection" in row["fields"]["description"]:
            location_type = "DELIVERY_ONLY"
        else:
            location_type = "OPEN"
        if "hours" in row["fields"]:
            hours_of_operation = get_hours(
                row["fields"]["hours"]["sys"]["id"], store_details["includes"]
            )
        else:
            hours_of_operation = "<MISSING>"
        latitude = row["fields"]["addressLocation"]["lat"]
        longitude = row["fields"]["addressLocation"]["lon"]
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                locator_domain,
                page_url,
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
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
