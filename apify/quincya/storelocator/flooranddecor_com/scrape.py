import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("flooranddecor_com")


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


def fetch_data():

    base_link = "https://www.flooranddecor.com/view-all-stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "openingHours" in str(script):
            script = str(script)
            break

    all_links = re.findall(
        r"https://www.flooranddecor.com/store\?StoreID=[0-9]+", script
    )

    data = []

    for link in all_links:
        logger.info(link)

        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        if item.find(class_="store-coming-soon-banner"):
            continue

        locator_domain = "flooranddecor.com"
        location_name = item.find("h1").text.strip()

        street_address = item.find(
            "span", attrs={"itemprop": "streetAddress"}
        ).text.strip()
        city = (
            item.find("span", attrs={"itemprop": "addressLocality"})
            .text.replace(",", "")
            .strip()
        )
        state = item.find("span", attrs={"itemprop": "addressRegion"}).text.strip()
        zip_code = item.find("span", attrs={"itemprop": "postalCode"}).text.strip()
        country_code = "US"

        store_number = link.split("=")[-1]
        try:
            phone = item.find("span", attrs={"itemprop": "telephone"}).text.strip()
        except:
            phone = "<MISSING>"

        location_type = "<MISSING>"

        raw_hours = item.find_all(class_="store-hours store-hours-1")
        hours = ""
        hours_of_operation = ""

        try:
            for hour in raw_hours:
                hours = (
                    hours
                    + " "
                    + hour.text.replace("\t", "")
                    .replace("\n", " ")
                    .replace("PM", "PM ")
                    .replace("Hours", "")
                    .replace("ClosedSat ClosedSun", "Closed Sat Closed Sun")
                    .strip()
                )
            hours_of_operation = (re.sub(" +", " ", hours)).strip()
        except:
            pass
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"].strip()
        longitude = item.find("meta", attrs={"itemprop": "longitude"})[
            "content"
        ].strip()

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
