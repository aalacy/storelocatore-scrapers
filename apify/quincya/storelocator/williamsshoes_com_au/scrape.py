import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.williamsshoes.com.au/stockists/index/search?key=AIzaSyDXvUmKIobGzAnIGVlgYEPbw9z4RM7ikqU"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["results"]["results"]

    locator_domain = "https://www.williamsshoes.com.au"

    found = []
    for store in store_data:
        location_name = store["name"]
        raw_address = store["street"]
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        if len(street_address) < 6:
            street_address = " ".join(raw_address.split()[2:])

        if street_address in found:
            continue
        found.append(street_address)

        city = store["city"]
        state = store["state"]
        zip_code = store["postcode"]
        country_code = "AU"
        location_type = ""
        try:
            phone = store["phone"].split("/")[0]
        except:
            phone = ""
        hours_of_operation = (
            store["opening_hours"].replace("\r\n", "").replace("\n", " ").strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        if "permanently" in hours_of_operation.lower():
            continue
        link = "https://www.williamsshoes.com.au/store-locator"
        store_number = store["entity_id"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        if not store["is_active"]:
            location_type = "Closed"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
