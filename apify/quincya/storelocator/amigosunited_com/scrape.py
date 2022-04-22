import json
import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    base_link = (
        base_link
    ) = "https://www.amigosunited.com/RS.Relationshop/StoreLocation/GetAllStoresPosition?__RequestVerificationToken=ppJizUtmjqj_Mmnt_AYesvj-FCsVsSx1xRx6zQsoPycvZVLhrs8tvXdBQ8v1m3GMB-fxBmiqCawul5Qevc58GCYhQJs1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    time.sleep(3)

    base = BeautifulSoup(driver.page_source, "lxml")
    stores = json.loads(base.text)

    driver.close()

    locator_domain = "amigosunited.com"

    for store in stores:

        location_name = store["StoreName"]
        if location_name != "Amigos":
            continue
        try:
            street_address = (store["Address1"] + " " + store["Address2"]).strip()
        except:
            street_address = store["Address1"]
        city = store["City"]
        state = store["State"]
        zip_code = store["Zipcode"]
        country_code = "US"
        store_number = store["StoreID"]
        phone = store["PhoneNumber"]
        hours_of_operation = store["StoreHours"]
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        location_type = ""
        types = store["ServiceStores"]
        for raw in types:
            location_type = (location_type + ", " + raw["ServiceName"]).strip()
        location_type = location_type[1:].strip()

        link = "https://www.amigosunited.com/rs/StoreLocator?id=" + str(store_number)

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
