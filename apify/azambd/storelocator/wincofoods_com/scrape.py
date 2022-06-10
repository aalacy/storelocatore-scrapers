from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgFirefox

from sgscrape import simple_scraper_pipeline as sp

from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

log = sglog.SgLogSetup().get_logger(logger_name="wincofoods.com")


def fetch_data():
    x = 0
    while True:
        x = x + 1

        url = "https://www.wincofoods.com/stores/?coordinates=41.20605200836969,-110.02699584999999&zoom=6"

        with SgFirefox(driver_wait_timeout=80) as driver:

            if x == 1:
                driver.get_and_wait_for_request(url)

            soup = bs(driver.page_source, "lxml")
            grids = soup.find("div", class_="store-list__scroll-container").find_all(
                "li"
            )
            log.info(f"Total Locations: {len(grids)}")

        if len(grids) == 0:
            continue
        else:
            break

    with SgFirefox() as driver:
        for grid in grids:
            name = grid.find("span", {"class": "store-name"}).text.strip()
            number = grid.find(
                "span",
                attrs={"ng-if": "$ctrl.showStoreNumber && $ctrl.store.storeNumber"},
            ).text.strip()
            page_url = (
                "https://www.wincofoods.com/stores/"
                + name.split("\n")[0].replace(" ", "-").replace(".", "").lower()
                + "-"
                + number.split("\n")[0].split("#")[-1]
                + "/"
                + grid["id"].split("-")[-1]
            )

            try:
                driver.get_and_wait_for_request(page_url)
                log.info("Pull content => " + page_url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "store-details-store-hours__content")
                    )
                )
            except Exception:
                driver.get_and_wait_for_request(page_url)
                log.info("Pull content => " + page_url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "store-details-store-hours__content")
                    )
                )

            location_soup = bs(driver.page_source, "lxml")

            locator_domain = "wincofoods.com"
            location_name = location_soup.find("meta", attrs={"property": "og:title"})[
                "content"
            ]
            street_address = location_soup.find(
                "meta", attrs={"property": "og:street-address"}
            )["content"]
            city = location_soup.find("meta", attrs={"property": "og:locality"})[
                "content"
            ]
            state = location_soup.find("meta", attrs={"property": "og:region"})[
                "content"
            ]
            zip_postal = location_soup.find(
                "meta", attrs={"property": "og:postal-code"}
            )["content"]
            country_code = location_soup.find(
                "meta", attrs={"property": "og:country-name"}
            )["content"]
            store_number = location_name.split("#")[-1]
            phone = location_soup.find("meta", attrs={"property": "og:phone_number"})
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone["content"]
            location_type = "<MISSING>"
            latitude = location_soup.find(
                "meta", attrs={"property": "og:location:latitude"}
            )["content"]
            longitude = location_soup.find(
                "meta", attrs={"property": "og:location:longitude"}
            )["content"]

            hours = ""
            days = location_soup.find(
                "dl", attrs={"aria-label": "Store Hours"}
            ).find_all("dt")
            hours_list = location_soup.find(
                "dl", attrs={"aria-label": "Store Hours"}
            ).find_all("dd")

            for x in range(len(days)):
                day = days[x].text.strip()
                hour = hours_list[x].text.strip()
                hours = hours + day + " " + hour + ", "

            hours_of_operation = hours[:-2]

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": street_address,
                "state": state,
                "zip": zip_postal,
                "phone": phone,
                "location_type": location_type,
                "hours": hours_of_operation,
                "country_code": country_code,
            }


def scrape():
    log.info("Start Crawling wincofoods.com ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )
    pipeline.run()


scrape()
