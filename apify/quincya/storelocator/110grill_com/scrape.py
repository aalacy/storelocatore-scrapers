import json
import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.110grill.com/locations"

    options = uc.ChromeOptions()
    options.headless = True

    with uc.Chrome(
        driver_executable_path=ChromeDriverManager().install(), options=options
    ) as driver:
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        raw_data = base.find(id="popmenu-apollo-state").contents[0]
        js = (
            raw_data.split("STATE =")[1].split(']},"CustomPageSelectedLocation')[0]
            + "]}}"
        )
        store_data = json.loads(js)

        locator_domain = "https://www.110grill.com/"

        for loc in store_data:
            if "RestaurantLocation:" in loc:
                store = store_data[loc]
                location_name = store["name"]
                street_address = store["streetAddress"]
                city = store["city"]
                state = store["state"]
                zip_code = store["postalCode"]
                country_code = "US"
                phone = store["displayPhone"]
                location_type = "<MISSING>"
                store_number = store["id"]
                latitude = store["lat"]
                longitude = store["lng"]
                link = locator_domain + store["slug"]
                hours_of_operation = " ".join(store["schemaHours"])
                days = ["Su ", "Mo ", "Tu ", "We ", "Th ", "Fr ", "Sa "]
                for day in days:
                    if day not in hours_of_operation:
                        hours_of_operation = hours_of_operation + " " + day + "Closed"
                hours_of_operation = hours_of_operation.strip()

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
