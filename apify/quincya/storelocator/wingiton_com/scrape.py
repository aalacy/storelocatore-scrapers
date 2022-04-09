import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/13795/stores.js?callback=SMcallback2"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://wingiton.com/"

    stores = json.loads(base.text.split('stores":')[1].split("})")[0])

    for store in stores:
        location_name = store["name"]
        raw_address = store["address"].split(",")
        street_address = raw_address[0]
        city = location_name.split(",")[0]
        state = location_name.split(",")[1]
        zip_code = raw_address[2].split()[-1].strip()
        if not zip_code.isdigit():
            zip_code = ""
            if "1600 East" in street_address:
                zip_code = "07036"
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        location_type = ""
        latitude = store["latitude"]
        longitude = store["longitude"]

        raw_data = BeautifulSoup(store["description"], "lxml")
        hours_of_operation = (
            raw_data.p.text.split("Hours")[1]
            .split("Order")[0]
            .replace("\r\n", " ")
            .strip()
        )

        link = store["url"]

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
