import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("carters.com")


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

    base_link = "https://locations.carters.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    next_links = []
    final_links = []

    main_items = base.find_all(class_="ml_directory_index_wrapper_region")
    for main_item in main_items:
        main_link = base_link + main_item.a["href"]
        main_links.append(main_link)

    logger.info("Getting links ..")
    for main_link in main_links:
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="ml_directory_index_wrapper_region")
        for next_item in next_items:
            next_link = main_link + next_item.a["href"]
            next_links.append(next_link)

    for next_link in next_links:
        req = session.get(next_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        final_items = base.find_all(class_="location_name")
        for final_item in final_items:
            final_link = final_item.a["href"]

            if "http" not in final_link:
                final_link = "https:" + final_link
                final_links.append(final_link)

    data = []
    total_links = len(final_links)
    logger.info("Processing %s links .." % (total_links))
    for i, final_link in enumerate(final_links):
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")
        locator_domain = "carters.com"

        script = item.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)

        location_name = "Carter's " + store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]

        try:
            store_number = re.findall(r'storeid":"[0-9]+', str(item))[0].split(':"')[1]
        except:
            store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]
        if not phone:
            phone = "<MISSING>"

        hours_of_operation = ""
        raw_hours = store["openingHoursSpecification"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            if len(day[0]) != 1:
                day = " ".join(hours["dayOfWeek"])
            opens = hours["opens"]
            closes = hours["closes"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        data = [
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

        yield data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
