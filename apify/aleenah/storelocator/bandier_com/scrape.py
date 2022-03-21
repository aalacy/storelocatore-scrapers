import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bandier_com")


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


def fetch_data():
    # Your scraper here

    res = session.get("https://www.bandier.com/locations")
    soup = BeautifulSoup(res.text, "html.parser")
    divs = soup.find_all("div", {"class": "location-block__item"})
    all = []
    for div in divs:

        data = (
            div.text.replace("View on Google Maps", "")
            .strip()
            .replace("\n\n\n", "\n\n")
            .replace("\n\n", "\n")
            .replace(
                "Features: Parking, Coffee Dose Café,  and Studio B. Sign up for  workouts here",
                "",
            )
            .replace(". Curbisde pickup only", "")
            .replace(" NOW OPEN! Hours of operation ", "")
            .replace("Store Hours:", "")
            .strip()
        )
        if "coming soon" in data or "Closed for the season" in data:
            continue
        data = data.split("\n")
        tim = data[-1]
        loc = data[0]
        logger.info(loc)
        if "*Currently closed in light of COVID-19.*" in data[0]:
            tim += " *Currently closed in light of COVID-19.*"
            del data[0]
        addr = (
            str(div.find("address").find("p"))
            .replace("<p>", "")
            .replace("</p>", "")
            .split("<br/>")
        )
        if "*Currently closed in light of COVID-19.*" in addr[0]:
            addr = (
                str(div.find("address").find_all("p")[1])
                .replace("<p>", "")
                .replace("</p>", "")
                .split("<br/>")
            )
        if addr != ["None"]:

            street = addr[0].strip()
            phone = re.findall(r"([\d\-]+)", addr[-1])[-1]
            addr = addr[1].strip().split(",")
            city = addr[0]
            addr = addr[1].strip().split(" ")
            zip = addr[1]
            state = addr[0]
        else:
            ps = div.find_all("p")
            addr = str(ps[0])
            addr = addr.replace("<p>", "").replace("</p>", "").strip().split("<br/>")
            street = addr[0]
            addr = addr[1].strip().split(",")
            city = addr[0]
            addr = addr[1].strip().split(" ")
            zip = addr[1]
            state = addr[0]
            phone = ps[1].text.replace("T:", "").strip()
            tim = (
                ps[2].text.strip().replace("Store Hours:", "").replace("\n", "").strip()
            )

        logger.info(addr)
        all.append(
            [
                "https://www.bandier.com/locations",
                loc,
                street,
                city,
                state.strip(),
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim.replace("PMS", "PM, S"),  # timing
                "https://www.bandier.com/locations",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
