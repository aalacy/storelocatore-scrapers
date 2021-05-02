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

        if "https://www.grottopizza.com/grotto-gift-shop/" in a.get("href"):
            continue
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

    addrs = re.findall(r"(\nGrotto Pizza.*Delivery to:)", str(soup.text), re.DOTALL)[
        0
    ].split("Delivery to:")
    if addrs[-1].strip() == "":
        del addrs[-1]
    for addr in addrs:
        addr = addr.split("\n")
        del addr[0]
        if addr[-1].strip() == "":
            del addr[-1]

        loc = addr[0]
        del addr[0]
        add = addr[0].split("•")
        street = add[0].strip()
        city = add[1].split(",")[0].strip()
        state = add[1].split(",")[1].strip()
        del addr[0]
        phone = addr[0]
        del addr[0]
        if "Hours" not in addr[0]:
            del addr[0]
        tim = (
            ", ".join(addr)
            .replace("Hours:", "")
            .replace("Hours –", "")
            .replace("\xa0", "")
            .strip()
        )

        all.append(
            [
                "https://grottopizza.com",
                loc,
                street,
                city,
                state,
                "<MISSING>",
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
