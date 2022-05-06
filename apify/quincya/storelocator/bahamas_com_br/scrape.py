from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    base_link = "https://bahamas.com.br/lojas/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    locator_domain = "https://bahamas.com.br/"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="entry-title")
    for i in items:
        link = i.a["href"]
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")
        location_name = item.h1.text
        raw_address = item.find(
            class_="elementor-element elementor-element-ad63210 elementor-widget elementor-widget-text-editor"
        ).text.strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode.replace("CEP", "").strip()
        country_code = "BR"
        store_number = ""
        location_type = ""
        phone = item.find(
            class_="elementor-element elementor-element-70290f0 elementor-widget elementor-widget-text-editor"
        ).text.strip()
        hours_of_operation = (
            item.find(
                class_="elementor-element elementor-element-92d7138 elementor-widget elementor-widget-text-editor"
            )
            .text.replace("\r\n", " ")
            .strip()
        )
        latitude = ""
        longitude = ""
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
