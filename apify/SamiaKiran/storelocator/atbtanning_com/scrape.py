import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "atbtanning_com"
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
    url = "https://www.atbtanning.com/locations/"
    r = session.get(url, headers=headers)
    loclist = r.text.split("location_list = '")[1].split("';", 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["name"]
        store = loc["id"]
        lat = loc["latitude"]
        if not lat:
            lat = "<MISSING>"
        longt = loc["longitude"]
        if not longt:
            longt = "<MISSING>"
        title = loc["name"]
        link = loc["url"]
        link = "https://www.atbtanning.com" + link
        phone = loc["phone_numbers"]
        if not phone:
            phone = "<MISSING>"
        if "<MISSING>" not in phone:
            phone = str(phone).split(": '", 1)[1].split("'}", 1)[0]
        street = loc["address"]["street_1"]
        city = loc["address"]["city"]
        state = loc["address"]["state"]
        pcode = loc["address"]["zip"]
        hours = loc["weekday_hours"] + " " + loc["weekend_hours"].replace("<br>", " ")

        data.append(
            [
                "https://www.atbtanning.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
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
