from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    base_link = "https://www.jackscarpet.com/location"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "html.parser")

    locator_domain = "jackscarpet.com"
    location_name = base.find("h1").text.strip()
    raw_data = list(base.find(id="page300_htmltext1").stripped_strings)
    street_address = raw_data[0]
    city = raw_data[1][: raw_data[1].find(",")].strip()
    state = raw_data[1][raw_data[1].find(",") + 1 : raw_data[1].rfind(" ")].strip()
    zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = list(base.find(id="page300_htmltext2").stripped_strings)[0]
    location_type = ""
    hours_of_operation = " ".join(
        list(base.find(id="page300_htmltext5").stripped_strings)[:-1]
    ).replace("\t", "")

    map_link = base.find(id="page300_htmltext1").a["href"]
    latitude = map_link.split("@")[1].split(",")[0]
    longitude = map_link.split("@")[1].split(",")[1]

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
