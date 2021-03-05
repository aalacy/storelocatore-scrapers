import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("wagamama_com")


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

    base_link = "https://www.wagamama.com/restaurants"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "wagamama.com"

    main_links = []
    final_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = "https://www.wagamama.com/restaurants/" + main_item["href"]
        count = main_item["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Teaser-titleLink")
        for next_item in next_items:
            next_link = "https://www.wagamama.com/restaurants/" + next_item["href"]
            final_links.append(next_link)

    for link in final_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "Wagamama " + base.h1.text.title()
        street_address = base.find(itemprop="streetAddress")["content"]
        city = base.find(class_="c-address-city").text.strip()
        state = "<MISSING>"
        zip_code = base.find(itemprop="postalCode").text.strip()
        country_code = "GB"
        store_number = "<MISSING>"
        phone = base.find(itemprop="telephone").text.strip()
        if not phone:
            phone = "<MISSING>"
        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]
        location_type = ""
        feats = base.find_all(itemprop="amenityFeature")
        for feat in feats:
            location_type = location_type + ", " + feat.text
        location_type = location_type[2:].strip()
        if not location_type:
            location_type = "<MISSING>"
        hours_of_operation = " ".join(
            list(base.find(class_="c-hours-details").tbody.stripped_strings)
        )

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
