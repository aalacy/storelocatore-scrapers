import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup


website = "steakescape_com"
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
    url = "https://steakescape.com/df-data/scripts/stores.js"
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc["name"]
        link = loc["file"]
        link = "https://steakescape.com/df-data/copy/locations/" + link
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        templist = soup.find("div", {"class": "two_col_15"}).findAll("p")

        if len(templist) > 2:
            address = templist[1].text.split("\n")
            if len(address) > 2:
                city = address[2].split(",", 1)[0]
            else:
                city = address[1].split(",", 1)[0]
            street = address[0]
            phone = templist[2].text
        else:
            phone = "<MISSING>"
            street = "<MISSING>"
            city = templist[1].text.split(",", 1)[0]
        lat = loc["lat"]
        longt = loc["lon"]
        state = loc["state"]
        pcode = loc["zip"]

        data.append(
            [
                "https://steakescape.com/",
                "https://steakescape.com/locations/",
                title.strip(),
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                "US",
                "<MISSING>",
                phone.strip(),
                "<MISSING>",
                lat,
                longt,
                "<MISSING>",
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
