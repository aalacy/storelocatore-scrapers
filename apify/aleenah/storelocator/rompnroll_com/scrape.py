import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rompnroll_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all = []


def fetch_data():
    # Your scraper here

    res = session.get("https://rompnroll.com/locations")
    soup = BeautifulSoup(res.text, "html.parser")
    divs = soup.find_all("div", {"class": "card-body"})
    logger.info(len(divs))
    del divs[4]  # singapore

    for div in divs:
        lis = div.find_all("li")
        logger.info(len(lis))
        for li in lis:

            if '<span style="">' in str(li):
                logger.info("in")
                continue

            url = li.find("a").get("href")
            logger.info(url)
            res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            loc = soup.find("h1").text
            if "closing" in loc.lower():
                continue
            data = str(soup)
            divs = soup.find_all("div", {"class": "card-body"})
            all.append(
                [
                    "https://rompnroll.com",
                    re.findall(r'"name":"([^"]+)"', data)[0],
                    re.findall(r'"streetAddress":"([^"]+)"', data)[0],
                    re.findall(r'"addressLocality":"([^"]+)"', data)[0],
                    re.findall(r'"addressRegion":"([^"]+)"', data)[0],
                    re.findall(r'"postalCode":"([^"]+)"', data)[0],
                    "US",
                    "<MISSING>",  # store #
                    re.findall(r'"telephone":"([^"]+)"', data)[0],  # phone
                    re.findall(r'"@type":"([^"]+)"', data)[0],  # type
                    re.findall(r'"latitude":"([^"]+)"', data)[0],  # lat
                    re.findall(r'"longitude":"([^"]+)"', data)[0],  # long
                    "<MISSING>",  # timing
                    url,
                ]
            )
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
