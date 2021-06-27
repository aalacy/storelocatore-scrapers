import csv
import ssl
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("dickeys_com")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


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

    base_link = "https://www.dickeys.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.dickeys.com/"

    all_links = []

    main_items = base.find(
        class_="style__StyledSearchByState-sc-1hzbtfv-1 kmMKLM"
    ).find_all("a")
    for main_item in main_items:
        main_link = locator_domain + main_item["href"]
        logger.info(main_link)

        main_status = False
        for i in range(10):
            req = session.get(main_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            next_items = base.find_all(class_="state-city__item")
            if len(next_items) > 0:
                main_status = True
                break

        if not main_status:
            logger.info("Unexpected error here!")
            raise

        for next_item in next_items:
            next_link = (locator_domain + next_item.a["href"]).replace("//loc", "/loc")

            next_status = False
            for i in range(10):
                try:
                    next_req = session.get(next_link, headers=headers)
                except:
                    break
                next_base = BeautifulSoup(next_req.text, "lxml")
                final_items = next_base.find_all(class_="store-info__inner")
                if len(final_items) > 0:
                    next_status = True
                    break

            if not next_status:
                continue

            for item in final_items:
                final_link = (locator_domain + item.a["href"]).replace("//loc", "/loc")
                if final_link in all_links:
                    continue
                all_links.append(final_link)

                location_name = item.a.text.strip()
                raw_address = item.find(
                    class_="Typography__P2-sc-11outmd-1 dqthKE store-info__address"
                ).text.split(",")
                street_address = (
                    (" ".join(raw_address[:-2]).strip())
                    .replace("Fairfield OH", "")
                    .replace("  ", " ")
                    .strip()
                )
                city = raw_address[-2].strip()
                state = raw_address[-1].strip()[:-6].strip()
                zip_code = raw_address[-1][-6:].strip()
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = item.find(
                    class_="Typography__P2-sc-11outmd-1 dqthKE store-info__telephone"
                ).a.text.strip()
                if not phone:
                    phone = "<MISSING>"

                try:
                    hours_of_operation = " ".join(
                        list(
                            item.find(class_="store-info__time")
                            .find_previous("div")
                            .stripped_strings
                        )
                    )
                except:
                    hours_of_operation = "<MISSING>"
                latitude = "<INACCESSIBLE>"
                longitude = "<INACCESSIBLE>"

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

    if (
        "https://www.dickeys.com/locations/New-York/Brooklyn/1683-brooklyn"
        not in all_links
    ):
        ny_link = "https://www.dickeys.com/locations/New-York/"
        driver = SgChrome(user_agent=user_agent).driver()
        driver.get(ny_link)
        time.sleep(5)
        ny = driver.find_element_by_xpath("//a[contains(text(), 'Brooklyn')]")
        ny.click()
        time.sleep(5)
        next_base = BeautifulSoup(driver.page_source, "lxml")
        final_items = next_base.find_all(class_="store-info__inner")

        for item in final_items:
            final_link = (locator_domain + item.a["href"]).replace("//loc", "/loc")

            location_name = item.a.text.strip()
            raw_address = item.find(
                class_="Typography__P2-sc-11outmd-1 dqthKE store-info__address"
            ).text.split(",")
            street_address = (
                (" ".join(raw_address[:-2]).strip())
                .replace("Fairfield OH", "")
                .replace("  ", " ")
                .strip()
            )
            city = raw_address[-2].strip()
            state = raw_address[-1].strip()[:-6].strip()
            zip_code = raw_address[-1][-6:].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.find(
                class_="Typography__P2-sc-11outmd-1 dqthKE store-info__telephone"
            ).a.text.strip()
            if not phone:
                phone = "<MISSING>"

            try:
                hours_of_operation = " ".join(
                    list(
                        item.find(class_="store-info__time")
                        .find_previous("div")
                        .stripped_strings
                    )
                )
            except:
                hours_of_operation = "<MISSING>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"

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
        driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
