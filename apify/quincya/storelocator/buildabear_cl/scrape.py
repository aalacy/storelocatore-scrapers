from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.buildabear.cl/tiendas-build-a-bear/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="wpb_text_column wpb_content_element")
    locator_domain = "https://www.buildabear.cl"

    for item in items:
        location_name = item.h3.text.strip()
        addr = parse_address_intl(item.a.text)
        street_address = addr.street_address_1
        city = addr.city.replace(".", "")
        state = ""
        if addr.state:
            state = addr.state.replace(".", "")
        zip_code = addr.postcode
        country_code = "Chile"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find_all("a")[1].text.strip()
        if "fono" in phone:
            phone = item.find_all("a")[2].text.strip()
        hours_of_operation = " ".join(list(item.table.stripped_strings))
        latitude = ""
        longitude = ""
        map_link = item.a["href"]
        if "@" in map_link:
            at_pos = map_link.rfind("@")
            latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
            longitude = map_link[
                map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
            ].strip()

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
                raw_address=item.a.text,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
