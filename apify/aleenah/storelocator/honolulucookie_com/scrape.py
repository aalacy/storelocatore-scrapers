import csv
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("honolulucookie_com")


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
    res = session.get("https://www.honolulucookie.com/content/store-locations.asp")
    soup = BeautifulSoup(res.text, "html.parser")
    stores = soup.find_all("div", {"class": "location-section"})
    del stores[0]
    for store in stores:
        uls = store.find_all("ul")
        for ul in uls:
            lis = ul.find_all("li")

            a = lis[0].find("a")
            loc = a.text
            lat, long = re.findall(r"/@(-?[\d\.]+),(-?[\d\.]+)", a.get("href"))[0]
            street = lis[1].text
            if "Caesars Palace®" in street:
                loc += " " + "Caesars Palace®"
                street = lis[2].text
                del lis[0]

            csz = lis[2].text.strip().split(",")
            if len(csz) == 1:
                csz = lis[3].text.strip().split(",")
                if len(csz) == 1:
                    city = state = zip = "<MISSING>"
                else:
                    street += " " + lis[2].text.strip()
                    city = csz[0]
                    logger.info(csz)
                    csz = csz[1].strip().split(" ")
                    state = csz[0]
                    zip = csz[1]
            else:
                city = csz[0]
                logger.info(csz)
                csz = csz[1].strip().split(" ")
                state = csz[0]
                zip = csz[1]

            if "Ph" in lis[3].text:
                phone = re.findall(r"([\d \)\(\-]+)", lis[3].text)[0]
            else:
                if "Ph" in lis[4].text:
                    phone = re.findall(r"([\d \)\(\-]+)", lis[4].text)[0]
                else:
                    phone = "<MISSING>"
            del lis[0]  # link
            del lis[0]  # street
            del lis[0]  # state,city,zip
            del lis[0]  # phone

            tim = ""
            for li in lis:
                if "ph:" in li.text.lower():
                    continue
                tim += li.text.strip() + " "
            tim = tim.strip()

            all.append(
                [
                    "https://www.honolulucookie.com",
                    loc,
                    street,
                    city,
                    state,
                    zip,
                    "US",
                    "<MISSING>",  # store #
                    phone.strip(),  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    tim,  # timing
                    "https://www.honolulucookie.com/content/store-locations.asp",
                ]
            )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
