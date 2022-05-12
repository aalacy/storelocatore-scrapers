import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bakkerbart.nl/winkels"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.bakkerbart.nl"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="stores").find_all(class_="item")
    for item in items:

        link = item.a["href"]

        location_name = item.find(class_="store-name").text
        street_address = item.find(attrs={"itemprop": "streetAddress"}).text.strip()
        city = item.find(attrs={"itemprop": "addressLocality"}).text.strip()
        state = ""
        zip_code = item.find(attrs={"itemprop": "postalCode"}).text.strip()
        country_code = "NL"
        phone = item.find(attrs={"itemprop": "telephone"}).text.strip()

        store_number = item["data-store-id"]
        location_type = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
        store = json.loads(script)

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        hours_of_operation = " ".join(
            list(
                base.find(
                    class_="block block-store-openings clearfix"
                ).table.stripped_strings
            )
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
