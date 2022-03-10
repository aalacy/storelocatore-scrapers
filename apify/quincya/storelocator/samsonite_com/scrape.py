import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-GetNearestStores?format=ajax&countryCode=&distanceUnit=mi&maxResults=10000&postalCode=&otherpostal=&maxdistance=10000"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["stores"]

    locator_domain = "samsonite.com"

    for store in stores:
        location_name = store["name"]
        raw_address = (store["address1"] + " " + store["address2"]).strip()
        street_address = raw_address

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]

        city = store["city"]
        state = store["stateCode"]
        zip_code = store["postalCode"]
        country_code = store["countryCode"]
        store_number = store["storeid"]
        location_type = store["storeType"]
        phone = store["phone"]

        if "closed" in location_name.lower():
            hours_of_operation = "Closed"
        else:
            hours_of_operation = ""
            raw_hours = store["storeHours"]
            hours = list(BeautifulSoup(raw_hours, "lxml").stripped_strings)
            for hour in hours:
                if "hours" not in hour.lower():
                    hours_of_operation = (
                        hours_of_operation + " " + re.sub(", .+: ", " ", hour)
                    ).strip()
            hours_of_operation = (
                hours_of_operation.replace(">", "").replace(" /li>", "").strip()
            )

        latitude = store["latitude"]
        longitude = store["longitude"]
        link = (
            "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-Details?StoreID="
            + store_number
        )

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
