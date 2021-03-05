import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("bertuccis.com")


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

    base_link = "https://locations.bertuccis.com/us"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    final_links = []

    main_items = base.find_all(class_="c-directory-list-content-item")
    for main_item in main_items:
        main_link = "https://locations.bertuccis.com/" + main_item.a["href"]
        count = (
            main_item.find(class_="c-directory-list-content-item-count")
            .text.replace("(", "")
            .replace(")", "")
            .strip()
        )
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="c-directory-list-content-item")
        if next_items:
            for next_item in next_items:
                main_link = (
                    "https://locations.bertuccis.com/" + next_item.a["href"]
                ).replace("../", "")
                count = (
                    next_item.find(class_="c-directory-list-content-item-count")
                    .text.replace("(", "")
                    .replace(")", "")
                    .strip()
                )
                if count == "1":
                    final_links.append(main_link)
                else:
                    raise

    data = []
    for final_link in final_links:
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "bertuccis.com"

        location_name = item.find(id="location-name").text.strip()
        if "COMING SOON" in location_name.upper():
            continue

        street_address = item.find(class_="c-address-street-1").text.strip()
        try:
            street_address = (
                street_address
                + " "
                + item.find(class_="c-address-street-2").text.strip()
            )
            street_address = street_address.strip()
        except:
            pass

        city = item.find(class_="c-address-city").text.replace(",", "").strip()
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
        hours_of_operation = (
            item.find(class_="c-location-hours-details")
            .get_text(" ")
            .replace("Day of the Week Hours", "")
            .replace("  ", " ")
            .strip()
        )

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
