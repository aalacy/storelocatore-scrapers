import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.relaxandwax.com/JS/salons.js"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = (
        base.text.split("= ")[1]
        .strip()
        .replace("\n", "")
        .replace("// hold", "")
        .replace("//hold", "")
        .replace(" // ", "")
        .replace("\\r\\n", " ")
        .replace("Georgia ", "")
        .replace("Texas ", "")
        .replace("Idaho ", "")
        .replace("Florida ", "")
        .replace("// ", "")
        .replace("\\", "")
    )
    stores = json.loads(js)

    locator_domain = "relaxandwax.com"

    for store in stores:
        location_name = store["name"]
        if (
            "Johns Creek" in location_name
            and '//   "short":"Johns Creek"' in base.text.split("= ")[1]
        ):
            continue
        street_address = store["address"].replace("\r\n", " ")
        if not street_address:
            continue
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["tel"]
        hours_of_operation = ""
        raw_hours = store["hours"]
        for row in raw_hours:
            hours = row["day"] + " " + row["hours"]
            hours_of_operation = (hours_of_operation + " " + hours).strip()
        latitude = store["lat"]
        longitude = store["lon"]
        if street_address == "2013 Lucille Street":
            latitude = "32.8015855"
            longitude = "-96.8044824"
        link = "https://www.relaxandwax.com/" + store["url"]

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
