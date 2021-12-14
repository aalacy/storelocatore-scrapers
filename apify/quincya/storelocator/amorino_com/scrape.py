import json

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from unidecode import unidecode


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://www.amorino.com/stores/stores.json"
    stores = session.get(api_link, headers=headers).json()

    locator_domain = "https://www.amorino.com/"

    for store in stores:
        location_name = store["name"]
        if "coming soon" in location_name.lower():
            continue
        raw_address = store["adress"]
        addr = parse_address_intl(raw_address)

        street_address = addr.street_address_1
        city = addr.city
        zip_code = addr.postcode
        try:
            state = store["region"]
        except:
            state = ""
        country_code = store["iso"].upper()
        store_number = store["id"]
        geo = json.loads(store["location"])
        latitude = geo["lat"]
        longitude = geo["lng"]
        location_type = ""
        phone = store["phone"]
        if not phone:
            phone = store["google_phone"].replace("'", "").strip()

        try:
            raw_hours = json.loads(store["opening_hours"])
            hours_of_operation = " ".join(raw_hours["weekday_text"])
        except:
            hours_of_operation = ""

        dec_name = unidecode(location_name)
        link = "https://www.amorino.com/storelocator?store=" + dec_name.replace(
            "(", ""
        ).replace(")", "").strip().replace(" ", "%20").replace(
            "METZINGEN", "METZINGEN%20"
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
