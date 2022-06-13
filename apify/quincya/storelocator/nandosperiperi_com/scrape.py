import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.nandosperiperi.com/find"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.find(id="__NEXT_DATA__").contents[0])["props"][
        "pageProps"
    ]["allLocations"]["restaurants"]

    locator_domain = "nandosperiperi.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["streetAddress"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        country_code = "US"
        store_number = store["id"]
        location_type = ""
        phone = store["telephone"]

        hours_of_operation = ""
        raw_hours = store["hours"]
        for i in raw_hours:
            hours = raw_hours[i]
            day = hours["day"]
            opens = hours["from"]
            closes = hours["to"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        latitude = store["latitude"]
        longitude = store["longitude"]

        link = "https://www.nandosperiperi.com/find/" + store["slug"]

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
