import json

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_link = "https://www.mec.ca/en/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.mec.ca"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="StoreCard_name__DshDi")
    for item in items:
        link = locator_domain + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        hours_of_operation = " ".join(
            list(base.find(id="main-content").table.tbody.stripped_strings)
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
