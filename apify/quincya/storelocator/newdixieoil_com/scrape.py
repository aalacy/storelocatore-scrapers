from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    base_link = "https://newdixieoil.com/new-dixie-mart-locations.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.article.find_all("tr")[1:]

    for item in items:
        locator_domain = "newdixieoil.com"
        location_name = ""
        store_number = item.find_all("td")[0].text.strip()
        street_address = item.find_all("td")[1].text.replace("   ", "").strip()
        city = item.find_all("td")[2].text.replace("   ", "").strip()
        state = item.find_all("td")[3].text.strip()
        zip_code = item.find_all("td")[4].text.strip()
        country_code = "US"
        location_type = ""
        store_number = item.find_all("td")[0].text.strip()
        phone = item.find_all("td")[5].text.strip()
        latitude = ""
        longitude = ""
        hours_of_operation = ""

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
