import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "boyes_co_uk"
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
    url = "https://www.boyes.co.uk/storelocator/"
    r = session.get(url, headers=headers)
    loclist = r.text.split("stores      :")[1].split("}],", 1)[0]
    loclist = loclist + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["name"]
        store = loc["storelocator_id"]
        lat = loc["latitude"]
        longt = loc["longtitude"]
        title = loc["name"]
        link = loc["rewrite_request_path"]
        link = "https://www.boyes.co.uk/" + link + "/"
        phone = loc["phone"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        if not state:
            state = "<MISSING>"
        pcode = loc["zipcode"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hourlist = soup.find("div", {"id": "open_hour"}).findAll("tr")
        hours = ""
        for hour in hourlist:
            temp = hour.findAll("td")
            day = temp[0].text
            time = temp[1].text
            hours = hours + " " + day + " " + time
        data.append(
            [
                "https://www.boyes.co.uk/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "UK",
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
