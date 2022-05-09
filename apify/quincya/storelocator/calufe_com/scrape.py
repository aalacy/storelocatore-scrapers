from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://calufe.com/ubicaciones"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://calufe.com/"

    items = base.find_all(class_="project__title")

    for i in items:
        code = i["data-target"].replace("#", "")
        item = base.find(id=code)

        location_name = item.h5.text

        raw_data = list(item.find_all("p")[-1].stripped_strings)
        raw_address = " ".join(raw_data[:-3])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if "Córdoba" in location_name:
            city = "Córdoba"
        if "Xalapa" in location_name:
            city = "Xalapa"
        if "Cholula" in location_name:
            city = "Cholula"
        if "Veracruz" in location_name:
            city = "Veracruz"
        if "Carmen" in location_name:
            city = location_name
        if "Obregón" in street_address:
            city = "Obregón"
        if not city:
            city = raw_data[2].split(",")[0]
        if "Novillero" in city:
            city = "Veracruz"

        country_code = ""
        store_number = ""
        location_type = ""
        phone = raw_data[-2].replace("Tel.", "").strip()
        hours_of_operation = raw_data[-1]
        if ":0" in raw_data[-2]:
            hours_of_operation = " ".join(raw_data[-2:])
            phone = raw_data[-3].replace("Tel.", "").strip()
        if "Boca" in phone:
            phone = ""

        map_link = item.find(class_="btn btn-link")["href"]
        lat_pos = map_link.rfind("!3d")
        latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
        lng_pos = map_link.find("!2d")
        longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
