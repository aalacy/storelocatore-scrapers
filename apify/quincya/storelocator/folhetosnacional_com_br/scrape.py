from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://folhetosnacional.com.br/horario/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://folhetosnacional.com.br"

    items = base.find_all(class_="card")

    for item in items:
        location_name = item.h3.text.strip()
        city = item.find_previous(class_="mb-6").text
        state = item.find_previous("h2").text
        hours_of_operation = " ".join(
            list(item.find(class_="row days").stripped_strings)
        )

        link = locator_domain + item.find(class_="btn")["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = base.find(class_="text-address__two-line").text.strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        zip_code = addr.postcode
        country_code = "BR"
        store_number = ""
        location_type = ""
        phone = (
            base.find(class_="text-address__two-line")
            .find_next("p")
            .text.split(": ")[1]
            .strip()
        )
        map_link = base.find(
            class_="btn btn--yellow font-weight-bold btn--rounded btn--md"
        )["href"]
        geo = map_link.split("ion=")[1].split("&")[0].split(",")
        latitude = geo[0]
        longitude = geo[1]

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
