from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    prem_link = "https://scotiabank-mx.appspot.com/datos/premium.csv"
    trad_link = "https://scotiabank-mx.appspot.com/datos/tradicionales.csv"

    locator_domain = "https://www.scotiabank.com.mx/"

    req = session.get(prem_link, headers=headers)
    prem_base = BeautifulSoup(req.text, "lxml")

    req = session.get(trad_link, headers=headers)
    trad_base = BeautifulSoup(req.text, "lxml")

    prem_data = prem_base.text.split("\n")[1:]
    for row in prem_data:
        store = row.split("|")
        try:
            location_name = store[1].strip()
        except:
            continue
        street_num = store[3].strip()
        if street_num.isdigit():
            street_address = street_num + " " + store[2].strip()
        else:
            street_address = store[2].strip()
        city = store[6].strip()
        state = store[5].strip()
        zip_code = store[7].strip()
        country_code = "MX"
        store_number = store[0].strip()
        phone = store[-2].replace("Tel:", "").split("/")[0].strip()
        if not phone[-1:].isdigit():
            phone = ""
        location_type = "Sucursales Premium"
        hours_of_operation = "Lun-Vie: " + store[13].strip()
        sat = store[14].strip()
        if sat and sat != "null":
            hours_of_operation = hours_of_operation + " Sabatino: " + sat
        latitude = store[12].strip()
        longitude = store[11].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://www.scotiabank.com.mx/sucursales-cajeros.aspx",
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

    trad_data = trad_base.text.split("\n")[1:]
    for row in trad_data:
        store = row.split("|")
        try:
            location_name = store[1].strip()
        except:
            continue
        street_num = store[3].strip()
        if street_num.isdigit():
            street_address = street_num + " " + store[2].strip()
        else:
            street_address = store[2].strip()
        city = store[-1].strip()
        state = store[5].strip()
        zip_code = store[6].strip()
        country_code = "MX"
        store_number = store[0].strip()
        phone = store[-2].replace("Tel:", "").split("/")[0].strip()
        if not phone[-1:].isdigit():
            phone = ""
        location_type = "Sucursales"
        hours_of_operation = "Lun-Vie: " + store[12].strip()
        sat = store[13].strip()
        if sat and sat != "null":
            hours_of_operation = hours_of_operation + " Sabatino: " + sat
        latitude = store[11].strip()
        longitude = store[10].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://www.scotiabank.com.mx/sucursales-cajeros.aspx",
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
