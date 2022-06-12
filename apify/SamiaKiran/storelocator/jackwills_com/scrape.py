import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "jackwills_com"
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
    pattern = re.compile(r"\s\s+")
    if True:
        url = "https://www.jackwills.com/stores/search?countryName=United%20Kingdom&countryCode=GB&lat=0&long=0&sd=500"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"id": "StoreFinderResultsListing"}).findAll(
            "div", {"class": "StoreFinderStore"}
        )
        for link in linklist:
            lat = link["data-latitude"]
            longt = link["data-longitude"]
            store = link["data-store-code"]
            link = link.find("a", {"class": "StoreFinderResultsDetailsLink"})[
                "href"
            ].replace("..", "https://www.jackwills.com")
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            loc = soup.find("div", {"id": "StoreDetailsContainer"})
            title = loc.find("h1").text.strip()
            temp = (
                loc.find("div", {"id": "StoreDetailsText"})
                .findAll("div", {"class": "StoreFinderList"})[2]
                .text.strip()
            )
            temp = re.sub(pattern, "\n", temp).split("\n")
            if len(temp) > 3:
                street = temp[0] + " " + temp[1]
                city = temp[2]
                pcode = temp[3]
            else:
                street = temp[0]
                city = temp[1]
                pcode = temp[2]
            hourlist = loc.findAll("meta", {"itemprop": "openingHours"})
            hours = ""
            for hour in hourlist:
                hours = hours + " " + hour["content"]
            if not hours:
                hours = "<MISSING>"
            state = "<MISSING>"
            phone = loc.find("span", {"itemprop": "telephone"}).text.strip()
            if not phone:
                phone = "<MISSING>"
            final_data.append(
                [
                    "https://www.jackwills.com/",
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
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
