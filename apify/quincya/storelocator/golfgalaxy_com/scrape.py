import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("golfgalaxy_com")


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

    base_link = "https://stores.golfgalaxy.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find(class_="contentlist").find_all("li")
    for main_item in main_items:
        main_link = main_item.a["href"]
        main_links.append(main_link)

    final_links = []
    for main_link in main_links:
        logger.info("Processing State: " + main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find(class_="contentlist").find_all("li")
        for next_item in next_items:
            next_link = next_item.a["href"]
            logger.info("Processing City: " + next_link)

            next_req = session.get(next_link, headers=headers)
            next_base = BeautifulSoup(next_req.text, "lxml")

            final_items = next_base.find_all(
                "span", attrs={"itemprop": "streetAddress"}
            )
            for final_item in final_items:
                final_link = final_item.find("a", attrs={"linktrack": "Landing page"})[
                    "href"
                ]
                final_links.append(final_link)

    data = []
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "golfgalaxy.com"

        location_name = item.find("h1").text.strip().title()
        logger.info(location_name)

        try:
            street_address = (
                re.findall(r"address2 : '[0-9].+'", str(item))[0][:-1]
                .split("'")[1]
                .strip()
            )
        except:
            street_address = (
                item.find(
                    "meta", attrs={"property": "business:contact_data:street_address"}
                )["content"]
                .replace("Burlington Square,", "")
                .strip()
            )
            if "shoppers world" in street_address.lower():
                street_address = item.find(class_="contact_info").span.text.strip()

        city = item.find("meta", attrs={"property": "business:contact_data:locality"})[
            "content"
        ]
        state = item.find("meta", attrs={"property": "business:contact_data:region"})[
            "content"
        ]
        zip_code = item.find(
            "meta", attrs={"property": "business:contact_data:postal_code"}
        )["content"]
        country_code = item.find(
            "meta", attrs={"property": "business:contact_data:country_name"}
        )["content"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(
            "meta", attrs={"property": "business:contact_data:phone_number"}
        )["content"]
        if not phone:
            phone = "<MISSING>"
        latitude = item.find("meta", attrs={"property": "place:location:latitude"})[
            "content"
        ]
        longitude = item.find("meta", attrs={"property": "place:location:longitude"})[
            "content"
        ]

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="store-hours").ul.stripped_strings)
            )
        except:
            hours_of_operation = "<MISSING>"

        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
