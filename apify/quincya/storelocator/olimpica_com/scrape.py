from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.olimpica.info/landing/domicilios/index.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.olimpica.com/"

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    city_list = base.find(class_="form-control").find_all("option")[1:]

    for city_row in city_list:
        city = city_row["value"]
        payload = {"paises[]": city}
        response = session.post(base_link, headers=headers, data=payload)
        base = BeautifulSoup(response.text, "lxml")

        items = base.find(class_="table horarios").find_all("tr")[1:]

        for item in items:
            location_name = item.find("td", attrs={"data-title": "Nombre"}).text
            street_address = item.find("td", attrs={"data-title": "Dirección"}).text
            if "direccion" in street_address:
                continue
            state = ""
            zip_code = ""
            country_code = "CO"
            store_number = ""
            location_type = ""
            phone = item.find("td", attrs={"data-title": "Directo"}).text
            if not phone:
                phone = item.find("td", attrs={"data-title": "Whatsapp"}).text
            if phone == "0" or phone == "n/a":
                phone = ""
            if "TIENE" in phone:
                phone = ""
            phone = (
                phone.split("-")[0].split("\n")[0].split("/")[0].split("EXT")[0].strip()
            )
            hours_of_operation = ""
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
