import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests


logger = SgLogSetup().get_logger("petsmart_ca")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    data = []
    # CA stores
    url = "https://www.petsmart.ca/stores/ca/"
    u = "https://www.petsmart.ca/"
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store = soup.find("div", class_="all-states-list container")
    str = store.find_all("a")
    for i in str:
        newurl = i["href"]
        logger.info(newurl)
        page = session.get(newurl)
        soup = BeautifulSoup(page.content, "html.parser")
        store = soup.find_all("a", class_="store-details-link")
        for j in store:
            ul = u + j["href"]
            if "closed" in ul.lower():
                continue
            page = session.get(ul)
            soup = BeautifulSoup(page.content, "html.parser")
            div = soup.find("div", class_="store-page-details")
            try:
                loc = div.find("h1").text
                if "closed" in loc.lower():
                    continue
            except:
                continue
            ph = div.find("p", class_="store-page-details-phone").text.strip()
            addr = (
                div.find("p", class_="store-page-details-address")
                .text.strip()
                .split("\n")
            )
            if len(addr) == 2:
                street = addr[0]
                addr = addr[1].strip().split(",")
            elif len(addr) > 2:
                add = addr[-1]
                del addr[-1]
                street = " ".join(addr)
                addr = add.strip().split(",")

            cty = addr[0]
            addr = addr[1].strip().split(" ")
            sts = addr[0]
            del addr[0]
            zcode = " ".join(addr).strip()
            try:
                hours = soup.find(
                    "div",
                    class_="store-page-details-hours-mobile visible-sm visible-md ui-accordion ui-widget ui-helper-reset",
                ).text
            except:
                hours = soup.find(
                    "div",
                    class_="store-page-details-hours-mobile visible-sm visible-md",
                ).text
            hours = hours.strip().replace("\n\n", "").replace("\n", "")
            for day in ["MON", "TUE", "THU", "WED", "FRI", "SAT", "SUN"]:
                if day not in hours:
                    hours = hours.replace("TODAY", day)
            lat, long = re.findall(
                r"center=([\d\.]+),([\-\d\.]+)",
                soup.find("div", class_="store-page-map mapViewstoredetail")
                .find("img")
                .get("src"),
            )[0]

            data.append(
                [
                    "https://www.petsmart.ca/",
                    ul.replace(u"\u2019", ""),
                    loc.replace(u"\u2019", "").strip(),
                    street.replace(u"\u2019", ""),
                    cty.replace(u"\u2019", ""),
                    sts.replace(u"\u2019", ""),
                    zcode.replace(u"\u2019", ""),
                    "CA".replace(u"\u2019", ""),
                    j["id"].replace(u"\u2019", ""),
                    ph.replace(u"\u2019", ""),
                    "<MISSING>",
                    lat,
                    long,
                    hours.replace(u"\u2019", ""),
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
