import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

website = "pizzabolis_com"
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
    if True:
        data = []
        url = "https://www.pizzabolis.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", string=re.compile("Directions"))
        for link in linklist:
            url = link["href"]
            if "#" in url:
                continue
            r = session.get(url, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            loc = r.text.split("var $location = [")[1].split(",];var", 1)[0]
            lat = loc.split("lat ", 1)[1].split(":", 1)[1].split(",", 1)[0].strip()
            longt = loc.split(",lng ", 1)[1].split(":", 1)[1].split(",", 1)[0].strip()
            phone = (
                loc.split("phone ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            title = (
                loc.split("name ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            link = (
                loc.split("url ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            store = (
                loc.split("id ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            street = (
                loc.split("street ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            city = (
                loc.split("city ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            state = (
                loc.split("state ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            pcode = (
                loc.split("zip ", 1)[1]
                .split(":", 1)[1]
                .split(",", 1)[0]
                .replace('"', "")
                .strip()
            )
            hourlist = soup.find("div", {"id": "hours"}).find("ul").findAll("li")
            hours = ""
            for hour in hourlist:
                day = hour.find("span", {"class": "day"}).text
                open_time = hour.find("span", {"class": "open"}).text
                close_time = hour.find("span", {"class": "close"}).text
                hours = hours + day + " " + open_time + " " + close_time + " "
            data.append(
                [
                    "https://www.pizzabolis.com/",
                    url,
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


if __name__ == "__main__":
    scrape()
