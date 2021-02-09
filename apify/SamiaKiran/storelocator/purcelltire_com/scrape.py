import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "purcelltire_com"
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
        url = "https://www.purcelltire.com/Contact/Find-Us?nav=%2f"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "LocationListView"}).findAll(
            "div", {"class": "loclisting type0"}
        )
        for loc in loclist:
            temp = loc.find("div", {"id": "info"})
            store = loc["id"]
            title = temp.find("div", {"class": "locationInfo"}).find("strong").text
            address = (
                temp.find("div", {"class": "locationInfo"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street = address[2]
            city = address[3].split(",", 1)[0]
            address = address[3].split(",", 1)[1].split()
            state = address[0]
            pcode = address[1]
            link = temp.find("a")["href"]
            phone = (
                loc.find("div", {"class": "contactInfo"})
                .find("div", {"class": "locphone"})
                .find("a")
                .text
            )
            hours = loc.find("div", {"class": "locationhours"}).text.replace(
                "Hours", ""
            )
            hours = re.sub(pattern, "\n", hours).replace("\n", " ").strip()
            lat = loc.find("div", {"class": "locLink"}).find("span")["lat"]
            longt = loc.find("div", {"class": "locLink"}).find("span")["lon"]
            final_data.append(
                [
                    "https://www.purcelltire.com/",
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
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
