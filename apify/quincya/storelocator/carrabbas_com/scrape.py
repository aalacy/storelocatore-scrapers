import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("carrabbas.com")


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

    base_link = "https://locations.carrabbas.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link + "index.html", headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    final_links = []

    main_items = base.find_all(class_="Directory-listLink")
    for main_item in main_items:
        main_link = base_link + main_item["href"]
        count = main_item["data-count"].replace("(", "").replace(")", "").strip()
        if count == "1":
            final_links.append(main_link)
        else:
            main_links.append(main_link)

    for main_link in main_links:
        logger.info(main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find_all(class_="Directory-listLink")
        if next_items:
            for next_item in next_items:
                next_link = base_link + next_item["href"]
                count = (
                    next_item["data-count"].replace("(", "").replace(")", "").strip()
                )

                if count == "1":
                    final_links.append(next_link)
                else:
                    next_req = session.get(next_link, headers=headers)
                    next_base = BeautifulSoup(next_req.text, "lxml")

                    final_items = next_base.find_all(class_="Teaser-titleLink")
                    for final_item in final_items:
                        final_link = (base_link + final_item["href"]).replace("../", "")
                        final_links.append(final_link)
        else:
            final_items = base.find_all(class_="Teaser-titleLink")
            for final_item in final_items:
                final_link = (base_link + final_item["href"]).replace("../", "")
                final_links.append(final_link)

    data = []
    total_links = len(final_links)
    logger.info("Processing %s links .." % (total_links))
    for final_link in final_links:
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "carrabbas.com"

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

        city = item.find(class_="c-address-city").text.strip()
        state = item.find(class_="c-address-state").text.strip()
        zip_code = item.find(class_="c-address-postal-code").text.strip()
        country_code = "US"
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        try:
            phone = item.find("div", attrs={"itemprop": "telephone"}).text.strip()
            if not phone:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"

        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]

        try:
            hours_of_operation = " ".join(
                list(item.find(class_="c-hours-details").tbody.stripped_strings)
            )
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
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
