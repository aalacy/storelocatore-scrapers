import json
from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://frame.staples-wiki.de/finderend/js/store-data.js"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://staples.de/"

    js = (
        base.text.split("stores =")[1]
        .replace("},  },", "}  },")
        .replace("\n", "")
        .strip()
    )
    stores = json.loads(js)

    for store in stores:
        location_name = store["name"]
        raw_address = (
            " ".join(store["addressLines"]).replace("  ", " ").replace("  ", " ")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "Germany"
        phone = store["phoneNumber"]
        if not phone:
            if location_name == "Neu-Ulm":
                phone = "0731 20766-0"
        store_number = store["storeNumber"]
        location_type = ""
        latitude = store["coordinates"]["latitude"]
        longitude = store["coordinates"]["longitude"]
        hours_of_operation = store["page"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://staples.de/filial-finder.html",
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
