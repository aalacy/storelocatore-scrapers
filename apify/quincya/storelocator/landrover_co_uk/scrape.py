import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="landrover.co.uk")


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

    base_link = (
        "https://www.landrover.co.uk/retailers/retailer-opening-information.html"
    )

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found_poi = []

    locator_domain = "landrover.co.uk"

    items = base.find_all(class_="tg-yseo")

    for item in items:
        link = item.a["href"]
        log.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        if "page not found" in location_name.lower():
            continue
        try:
            base.find(class_="retailerContact__address1").text
        except:
            continue

        street_address = (
            base.find(class_="retailerContact__address1").text
            + " "
            + base.find(class_="retailerContact__address2").text
        ).strip()
        city = base.find(class_="retailerContact__locality").text.strip()
        state = "<MISSING>"
        zip_code = base.find(class_="retailerContact__postcode").text.strip()
        country_code = "GB"

        try:
            store_number = base.find(class_="primaryLinkWithStyle TargetLinks")[
                "href"
            ].split("dealerci=")[1]
        except:
            store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = base.find(class_="tel").text.strip()
            if not phone:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"

        if location_name + street_address in found_poi:
            continue
        found_poi.append(location_name + street_address)

        hours_of_operation = " ".join(list(base.table.stripped_strings))
        latitude = base.find(class_="retailerContact")["data-lat"]
        longitude = base.find(class_="retailerContact")["data-long"]

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
