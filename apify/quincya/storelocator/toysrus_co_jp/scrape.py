import json

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www2.toysrus.co.jp/storeinfo/?store_type%5B%5D=toy&store_type%5B%5D=baby&store_type%5B%5D=est&q="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www2.toysrus.co.jp"

    script = (
        str(base)
        .replace("\r\n", "")
        .replace("\t", "")
        .split("dataList = ")[1]
        .split(",];")[0]
        + "]"
    )
    stores = json.loads(script)

    for store in stores:
        location_name = store["name"]

        raw_address = store["address"]
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "Japan"
        store_number = store["slug"]
        if store["type"] == "est":
            location_type = "toy, baby"
        else:
            location_type = store["type"]
        phone = store["phone_number"]
        hours_of_operation = store["hours"]
        latitude = store["lat"]
        longitude = store["lng"]
        link = store["link"]

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
