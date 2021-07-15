import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("arbys.com")


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

    base_link = "https://locations.arbys.com/?_ga=2.162119932.1183880869.1626249434-1748791237.1623814424"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    main_items = base.find(class_="border-container-top").find_all(class_="ga-link")
    for main_item in main_items:
        main_link = main_item["href"]

        state_count = []
        logger.info("Processing: " + main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find(class_="border-container-top").find_all(class_="ga-link")
        for next_item in next_items:
            link = next_item["href"]
            next_req = session.get(link, headers=headers)
            next_base = BeautifulSoup(next_req.text, "lxml")

            other_links = next_base.find_all(class_="location-name ga-link")
            for other_link in other_links:
                link = other_link["href"]
                final_links.append(link)
                state_count.append(state_count)
        logger.info(len(state_count))

    logger.info("Processing %s links .." % (len(final_links)))
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "arbys.com"

        script = item.find("script", attrs={"type": "application/ld+json"}).contents[0]
        try:
            store = json.loads(script)[0]
        except:
            store = json.loads(script.split('"additiona')[0].strip()[:-1] + "}]")[0]
        try:
            location_name = item.find(class_="h2").text.strip()
        except:
            location_name = store["name"]
        street_address = store["address"]["streetAddress"].strip()
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        if not zip_code:
            zip_code = "<MISSING>"
        country_code = "US"
        try:
            location_type = ", ".join(
                list(item.find(class_="location-features-wrap mb-0").stripped_strings)
            )
        except:
            location_type = "<MISSING>"
        phone = store["address"]["telephone"]
        if not phone:
            phone = "<MISSING>"
        if not location_name:
            location_name = "<MISSING>"
        store_number = (
            item.find(class_="store-id").text.replace("Store ID:", "").strip()
        )
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        try:
            hours_of_operation = " ".join(list(item.find(class_="hours").stripped_strings))
        except:
            hours_of_operation = "<MISSING>"

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
