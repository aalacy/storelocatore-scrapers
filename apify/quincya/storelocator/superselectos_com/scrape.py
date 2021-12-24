import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.superselectos.com/Tienda/Sucursales"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.superselectos.com"

    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    items = base.table.find_all("tr")[1:]
    for item in items:
        location_name = item.td.text.strip()

        raw_address = item.find_all("td")[2].text.strip()
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "El Salvador"
        location_type = ""
        phone = item.find_all("td")[1].text.strip()
        hours_of_operation = item.find_all("td")[-1].text.strip()
        map_str = item.td.a["onclick"]
        store_number = map_str.split("_")[-1].split(")")[0]
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+, -[0-9]{2,3}\.[0-9]+", map_str)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if city:
            city = (
                city.replace("Cara Sucia", "")
                .replace("Etapa Ii", "")
                .replace(".", "")
                .strip()
            )
            if "La Libertad" in city:
                state = "La Libertad"
        if state:
            state = state.replace("Departamento De", "").strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
