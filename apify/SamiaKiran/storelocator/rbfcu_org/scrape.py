import csv
import re
from sgrequests import SgRequests
from sglogging import sglog


website = "rbfcu_org"
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
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    pattern = re.compile(r"\s\s+")
    url = "https://www.rbfcu.org/locations"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split("var locationRecord = ")[1:]
    pattern = re.compile(r"\s\s+")
    for loc in loclist:
        loc = (
            loc.split("additionalOptions: {", 1)[0]
            .replace("},", "")
            .replace("{", "")
            .replace("'", "")
            .strip()
        )
        loc = re.sub(pattern, "\n", loc)
        store = loc.split("recordId:", 1)[1].split(",", 1)[0].strip()
        title = (
            loc.split("locationName:", 1)[1]
            .split(",", 1)[0]
            .replace("&amp;", " ")
            .strip()
        )
        location_type = (
            loc.split("locationType:", 1)[1].split(",", 1)[0].split(".", 1)[0].strip()
        )
        lat = loc.split("latitude:", 1)[1].split(",", 1)[0].strip()
        longt = loc.split("longitude:", 1)[1].split(",", 1)[0].strip()
        hours = loc.split("lobbyHours:", 1)[1].split("driveThruHours:", 1)[0].strip()
        hours = hours.split("\n")
        weekday = hours[1].replace(",", "").replace("\n", "").strip()
        weekend = hours[2].replace(",", "").replace("\n", "").strip()
        if len(weekday) > 9:
            if len(weekend) < 9:
                weekend = ""
                weekday = weekday.split("weekday: ", 1)[1]
                hours = weekday + " " + weekend
            else:
                weekday = weekday.split("weekday: ", 1)[1]
                weekend = weekend.split("weekend: ", 1)[1]
                hours = weekday + " " + weekend
        elif len(weekend) > 9:
            if len(weekday) < 9:
                weekday = ""
                weekend = weekend.split("weekend: ", 1)[1]
                hours = weekday + " " + weekend
            else:
                weekday = weekday.split("weekday: ", 1)[1]
                weekend = weekend.split("weekend: ", 1)[1]
                hours = weekday + " " + weekend
        else:
            hours = "<MISSING>"
        street = loc.split("street:", 1)[1].split(",", 1)[0].strip()
        city = loc.split("city:", 1)[1].split(",", 1)[0].strip()
        state = loc.split("state:", 1)[1].split(",", 1)[0].strip()
        pcode = loc.split("zipcode:", 1)[1].split(",", 1)[0].strip()
        data.append(
            [
                "https://rbfcu.org/",
                "https://www.rbfcu.org/locations",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                "<MISSING>",
                location_type,
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


if __name__ == "__main__":
    scrape()
