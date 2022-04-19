from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://vips.com.mx/"

    store_link = "https://vips.com.mx/include/ubicaciones/restaurantes_lista.php?filter=&edo=ubicacion&lat=19.4268854&lng=-99.1680372"

    stores = session.get(store_link, headers=headers).json()

    for store in stores:
        location_name = store["name"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = ""
        phone = BeautifulSoup(store["phone"], "lxml").text.strip()
        hours_of_operation = (
            BeautifulSoup(store["horario"], "lxml").text.replace("Horario:", "").strip()
        )
        latitude = store["latitude"]
        longitude = store["longitude"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://vips.com.mx/restaurantes",
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
