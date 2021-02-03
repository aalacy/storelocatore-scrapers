import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("grottopizza_com")


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

    res = session.get("https://grottopizza.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")
    sa = soup.find("ul", {"class": "sub-nav grid-parent"}).find_all("a")
    logger.info(len(sa))
    for a in sa:
        res = session.get(a.get("href"))
        soup = BeautifulSoup(res.text, "html.parser")
        loc = soup.find("span", {"class": "italia white-text blocked"}).text
        addr = re.findall(
            r'<h4>[ ]+Address</h4><p>([^<]+)<span class="blocked">([^<]+)',
            str(soup).replace("\n", "").replace("\r", ""),
        )[0]
        street = addr[0].strip()
        addr = addr[1].strip().split(",")
        city = addr[0]
        addr = addr[1].strip().split(" ")
        state = addr[0]
        zip = addr[1]
        phone = soup.find("a", {"class": "callout-text phone-link"}).text
        tim = (
            soup.find("div", {"class": "et_pb_module et_pb_code et_pb_code_4"})
            .text.replace(
                "Dine-in Now Available!Reserve your table on our waitlist.", ""
            )
            .replace("Hours of Operation", "")
            .replace("\n", " ")
            .strip()
        )
        tim = (
            tim.encode("ascii", errors="ignore")
            .decode("ascii")
            .replace("AM  ", "AM - ")
            .replace("y T", "y - T")
            .replace("AM -   Su", "AM   Su")
            .replace("AM -    Su", "AM   Su")
            .replace("ySu", "y - Su")
        )
        logger.info(tim)
        all.append(
            [
                "https://grottopizza.com",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim.replace("Äì", "").replace("¬†", ""),  # timing
                a.get("href"),
            ]
        )

    res = session.get("https://grottopizzapa.com/?page_id=20")  # pensylvania locations
    soup = BeautifulSoup(res.text, "html.parser")
    addr = re.findall(
        r"<h3>([^<]+)<br/>([^<]+)<br/>([^<]+)</h3><p>[^<]+</p><p>([^<]+)</p>",
        str(soup)
        .replace("\n", "")
        .replace("\r", "")
        .replace("&amp; ", "")
        .replace("</strong>", "")
        .replace("<strong>", ""),
    )
    for add in addr:
        loc = add[0]
        tim = add[-1]
        phone = add[2]
        add = add[1].split("•")
        street = add[0]
        add = add[1].split(",")
        city = add[0]
        state = add[1].strip()
        zip = "<MISSING>"
        tim = (
            tim.encode("ascii", errors="ignore")
            .decode("ascii")
            .replace("AM  ", "AM - ")
            .replace("y T", "y - T")
            .replace("AM -   Su", "AM   Su")
            .replace("AM -    Su", "AM   Su")
            .replace("ySu", "y - Su")
        )
        logger.info(tim)

        all.append(
            [
                "https://grottopizza.com",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim,  # timing
                "https://grottopizzapa.com/?page_id=20",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
