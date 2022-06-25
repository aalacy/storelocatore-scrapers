import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "http://www.mobilyllc.com/wp-admin/admin-ajax.php?action=store_search&lat=29.7604267&lng=-95.3698028&search_radius=150&autoload=1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "mobilyllc.com"

    stores = json.loads(base.text.strip())

    for store in stores:
        location_name = "MobilyLLC - " + store["store"]
        street_address = (
            store["address"].replace("(Buda Town Center)", "").split("(Copa")[0].strip()
        )
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = store["city"]
        if "NEW HAVEN" in street_address:
            street_address = street_address.replace("NEW HAVEN", "").strip()
            city = "New Haven"
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = (
            store["hours"]
            .replace("day", "day ")
            .replace("PM", "PM ")
            .replace("AM", "AM ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        latitude = store["lat"]
        longitude = store["lng"]
        link = store["permalink"]

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
