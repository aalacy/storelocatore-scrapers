from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.masseyspizza.com/locations/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "masseyspizza.com"

    items = base.find(id="main-content").find_all(class_="et_pb_text_inner")

    for item in items:
        try:
            location_name = item.strong.text.strip()
        except:
            continue
        raw_address = list(item.stripped_strings)[1:]
        if "NOW OPEN" in raw_address[0] or "VILLE/WORTH" in raw_address[0]:
            raw_address.pop(0)
        for i, item in enumerate(raw_address):
            if (
                "Massey’s Pizza" in raw_address[i]
                or "View Map" in raw_address[i]
                or "ORDER" in raw_address[i]
            ):
                raw_address = raw_address[:i]
                break
        if "(" in raw_address[1]:
            phone = raw_address[1]
            street_address = raw_address[0].strip()
            hours_of_operation = " ".join(raw_address[2:])
        else:
            street_address = " ".join(raw_address[:2]).strip()
            phone = raw_address[2]
            hours_of_operation = " ".join(raw_address[3:])

        hours_of_operation = hours_of_operation.split("DINING")[0].strip()

        city = ""
        state = ""
        zip_code = ""
        country_code = "US"
        store_number = "<MISSING>"
        location_type = ""
        latitude = ""
        longitude = ""

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
