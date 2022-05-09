from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.lush.ch/info/ShopsinderSchweiz.aspx"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="store-wrapper")
    locator_domain = "https://www.lush.ch"

    for item in items:
        location_name = item.h3.text.strip()
        raw_address = item.find(class_="address-text").div.text
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if street_address.isdigit():
            zip_code = street_address
            street_address = raw_address.split(",")[0].strip()
        country_code = "CH"
        location_type = ""
        store_number = ""
        phone = item.a.text.replace("Tel", "").strip()
        latitude = ""
        longitude = ""
        hours_of_operation = " ".join(
            list(item.find(class_="hours-text").stripped_strings)
        )

        link = "https://www.lush.ch/info/ShopsinderSchweiz.aspx"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
