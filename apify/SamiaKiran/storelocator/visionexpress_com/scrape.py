import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "visionexpress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
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
    url = "https://www.visionexpress.com/opticians"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"stores":[')[1].split('],"queryParams"', 1)[0]
    loclist = "[" + loclist + "]"
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["storeName"]
        lat = loc["lat"]
        longt = loc["lon"]
        store = loc["code"]
        phone = loc["Phone1"]
        city = loc["town"]
        street = loc["streetName"]
        state = loc["province"]
        pcode = loc["postalCode"]
        ccode = loc["country"]
        link = (
            "https://www.visionexpress.com/opticians/"
            + city.lower()
            + "/"
            + loc["slug"]
        )
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hour_list1 = soup.find("div", {"class": "store-opening-hours__days"}).findAll(
            "dt"
        )
        hour_list2 = soup.find("div", {"class": "store-opening-hours__times"}).findAll(
            "dd"
        )
        hours = [i.text + " " + j.text for i, j in zip(hour_list1, hour_list2)]
        hours = " ".join(hours)
        data.append(
            [
                "https://www.visionexpress.com/",
                link,
                title.strip(),
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                ccode.strip(),
                store,
                phone.strip(),
                "<MISSING>",
                lat,
                longt,
                hours.strip(),
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
