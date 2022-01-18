import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.aki.com.ec/locales-aki/"

    locator_domain = "https://www.aki.com.ec/"
    country_code = "Ecuador"

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "newLocation =" in str(script):
            items = str(script).split("\n")

            for item in items:
                if "nombre" in item:
                    location_name = item.split("'")[1].split(',"')[0]
                elif "var lat" in item:
                    latitude = item.split("'")[1].split("'")[0].replace(",", ".")
                elif "var lng" in item:
                    longitude = item.split("'")[1].split("'")[0].replace(",", ".")
                elif "id:" in item:
                    store_number = item.split("'")[1].split("'")[0]
                elif "ciudad:" in item:
                    city = item.split("'")[1].split("'")[0].replace("-", " ").title()
                elif "telefonos" in item:
                    phone = item.split("'")[1].split("'")[0]
                    phone = (re.sub(" +", " ", phone)).strip()
                elif "slug:" in item:
                    link = (
                        "https://www.aki.com.ec/locales/"
                        + item.split("'")[1].split("'")[0]
                    )
                elif "horarios" in item:
                    hours_of_operation = BeautifulSoup(
                        item.split("'")[1].split("'")[0], "lxml"
                    ).text
                elif "direccion" in item:
                    raw_address = item.split("'")[1].split("'")[0]
                    addr = parse_address_intl(raw_address)
                    try:
                        street_address = (
                            addr.street_address_1 + " " + addr.street_address_2
                        )
                    except:
                        street_address = addr.street_address_1
                    state = addr.state
                    zip_code = addr.postcode
                elif "push(newLocation" in item:
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
                            location_type="",
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                            raw_address=raw_address,
                        )
                    )

                    break


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
