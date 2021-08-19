import csv
import json
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "myrentking_com"
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
    url = "https://www.myrentking.com/store_finder.html"
    r = session.get(url, headers=headers)
    loclist = r.text.split("var locations = [")[1].split(
        "// Render the locations using the array", 1
    )[0]
    loclist = loclist.replace("];", "")
    pattern = re.compile(r"\s\s+")
    loclist = re.sub(pattern, "\n", loclist)
    loclist = "[" + loclist.rsplit("},", 1)[0] + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["store_name"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        link = loc["url"]
        link = "https://www.myrentking.com/" + link
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        phone = (
            soup.find("div", {"id": "location-address-section"})
            .find("strong", {"class": "font-18"})
            .text.strip()
        )
        hourlist = (
            soup.find("div", {"id": "location-hours-section"})
            .find("table", {"class": "table table-responsive"})
            .findAll("tr")
        )
        hours = ""
        for hour in hourlist:
            temp = hour.findAll("td")
            day = temp[0].text
            time = temp[1].text.strip()
            hours = hours + " " + day + " " + time
        data.append(
            [
                "https://www.myrentking.com/",
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
