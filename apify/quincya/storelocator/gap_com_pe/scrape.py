import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.gap.com.pe/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.gap.com.pe/nuestras-tiendas"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    raw_data = (
        (str(base).split("coordenadastiendas =")[1].split("]}")[0][3:].strip() + "]")
        .replace("lat", '"lat"')
        .replace("lng", '"lng"')
    )

    geo_data = raw_data.split("];")[0].strip().split("},")
    stores = json.loads(raw_data.split('tiendas" :')[1])

    for i, store in enumerate(stores):
        location_name = store["nombre"]
        street_address = BeautifulSoup(store["direccion"], "lxml").text
        city = ""
        state = ""
        zip_code = ""
        country_code = "Peru"
        store_number = ""
        location_type = ""
        phone = store["telefono"]
        latitude = geo_data[i].split()[1].split(",")[0]
        longitude = geo_data[i].split()[-1].replace("}", "")
        hours_of_operation = BeautifulSoup(store["descripcion"], "lxml").text

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
