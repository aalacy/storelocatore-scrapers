import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("citizensbank_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://locations.citizensbank.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    final_links = []

    main_items = base.find_all(class_="c-directory-list-content-item-link")
    for main_item in main_items:
        main_link = base_link + main_item["href"]
        if main_link.count("/") == 5:
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for next_link in main_links:
        logger.info("Processing: " + next_link)
        req = session.get(next_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find_all(class_="c-directory-list-content-item")
        for next_item in next_items:
            count = (
                next_item.find(class_="c-directory-list-content-item-count")
                .text.replace("(", "")
                .replace(")", "")
            ).split()[0]
            link = (
                base_link
                + next_item.find(class_="c-directory-list-content-item-link")["href"]
            )
            if count == "1":
                final_links.append(link)
            else:
                next_req = session.get(link, headers=headers)
                next_base = BeautifulSoup(next_req.text, "lxml")

                other_links = next_base.find_all(
                    class_="c-location-grid-item-name-link"
                )
                for other_link in other_links:
                    link = base_link + other_link["href"].replace("../", "")
                    final_links.append(link)

    logger.info("Processing %s links .." % (len(final_links)))
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "citizensbank.com"

        city = (
            item.find("span", attrs={"itemprop": "addressLocality"})
            .text.replace(",", "")
            .strip()
        )
        location_name_geo = item.find(class_="location-name-geomodifier").text.strip()

        location_name = (
            item.find(class_="location-name-brand").text.strip()
            + " "
            + location_name_geo
        )

        street_address = (
            item.find(class_="c-address-street c-address-street-1")
            .text.replace("\u200b", "")
            .strip()
        )
        try:
            street_address = (
                street_address
                + " "
                + item.find(class_="c-address-street c-address-street-2")
                .text.replace("\u200b", "")
                .strip()
            )
            street_address = street_address.strip()
        except:
            pass

        state = item.find(class_="c-address-state").text.strip()
        zip_code = item.find(class_="c-address-postal-code").text.strip()
        country_code = "US"
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        try:
            phone = item.find(id="telephone").text.strip()
        except:
            phone = "<MISSING>"

        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]

        hours_of_operation = ""
        raw_hours = item.find(class_="c-location-hours-details")
        raw_hours = raw_hours.find_all("td")

        hours = ""
        hours_of_operation = ""

        try:
            for hour in raw_hours:
                hours = hours + " " + hour.text.strip()
            hours_of_operation = (re.sub(" +", " ", hours)).strip()
        except:
            pass
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        if (
            final_link
            == "https://locations.citizensbank.com/ri/warwick/300-quaker-ln-3817966.html"
        ):
            street_address = street_address.split("Suite")[0].strip()

        yield [
            locator_domain,
            final_link,
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
