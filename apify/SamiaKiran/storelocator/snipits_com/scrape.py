import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "snipits_com"
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
    if True:
        url = "https://www.snipits.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find("div", {"class": "locationResults"}).findAll(
            "div", {"class": "loc-result"}
        )
        for link in linklist:
            temp = link.find("h4").find("a")
            title = temp.text
            link = temp["href"]
            r = session.get(link, headers=headers, verify=False)
            loc = r.text.split('<script type="application/ld+json">')[1].split(
                " </script>", 1
            )[0]
            loc = json.loads(loc)
            phone = loc["telephone"]
            lat = loc["geo"]["latitude"]
            longt = loc["geo"]["longitude"]
            street = loc["address"]["streetAddress"]
            city = loc["address"]["addressLocality"]
            state = loc["address"]["addressRegion"]
            pcode = loc["address"]["postalCode"]
            ccode = loc["address"]["addressCountry"]
            location_type = loc["@type"]
            soup = BeautifulSoup(r.text, "html.parser")
            hourlist = soup.find("div", {"class": "div-block-26"}).findAll(
                "div", {"class": "r-nav-label"}
            )
            hours = ""
            for hour in hourlist:
                hour = hour.text
                hours = hours + " " + hour
            final_data.append(
                [
                    "https://www.snipits.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    "<MISSING>",
                    phone,
                    location_type,
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
