import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "dibellas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://api.chepri.io/dibellas/custom/dineengine/vendor/olo/restaurants?includePrivate=false"
        loclist = session.get(url, headers=headers).json()["restaurants"]
        for loc in loclist:
            link = loc["url"]
            title = loc["storename"]
            store = loc["id"]
            street = loc["streetaddress"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            phone = loc["telephone"]
            hours = "<INACCESSIBLE>"
            final_data.append(
                [
                    "https://www.dibellas.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "USA",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours.strip(),
                ]
            )
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
