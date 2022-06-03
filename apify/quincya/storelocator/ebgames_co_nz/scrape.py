import json
import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.ebgames.co.nz/stores"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    locator_domain = "https://www.ebgames.co.nz/"

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "AddressLine1" in str(script):
                script = str(script)
                break
        js = script.split('store-map",')[1].split(",\n")[0].strip()
        stores = json.loads(js)

        for store in stores:
            location_name = store["Name"]
            raw_address = (store["AddressLine1"] + " " + store["AddressLine2"]).strip()
            if "shop " in store["AddressLine1"].lower():
                street_address = store["AddressLine2"]
            else:
                street_address = raw_address
            street_address = street_address.split(", Auckland")[0]
            city = store["Suburb"].split(",")[-1].strip()
            state = store["State"]
            zip_code = store["Postcode"]
            country_code = "NZ"
            phone = store["Phone"]
            store_number = store["Id"]
            location_type = store["StoreTypeName"]
            latitude = store["Geolocation"]["Latitude"]
            longitude = store["Geolocation"]["Longitude"]
            link = "https://www.ebgames.co.nz/stores/store/" + store["StoreUrl"]
            hours_of_operation = ""

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
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
