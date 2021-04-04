import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "gebos_com"
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
    data = []
    url = "https://www.gebos.com/locationquery.php?formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc["title"]
        link = (
            "https://www.gebos.com/locations/"
            + title.split(",", 1)[0].replace(" ", "-").lower()
        )

        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postal"]
        try:
            hours = loc["hours1"] + " " + loc["hours2"]
        except:
            hours = loc["hours1"]
        data.append(
            [
                "https://www.gebos.com//",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
