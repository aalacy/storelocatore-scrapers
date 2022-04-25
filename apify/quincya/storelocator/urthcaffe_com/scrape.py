import json
import ssl

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.urthcaffe.com/"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    raw_data = base.find(id="popmenu-apollo-state").contents[0]
    js = raw_data.split("STATE =")[1].strip()[:-1]
    store_data = json.loads(js)

    for loc in store_data:
        if "RestaurantLocation:" in loc:
            store = store_data[loc]

            location_name = store["name"]
            street_address = store["streetAddress"].replace("\n", " ")
            city = store["city"]
            state = store["state"]
            zip_code = store["postalCode"]
            country_code = "US"
            location_type = "<MISSING>"
            phone = store["displayPhone"]
            hours_of_operation = " ".join(store["schemaHours"])
            link = base_link + store["slug"]
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]

            sgw.write_row(
                SgRecord(
                    locator_domain=base_link,
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

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
