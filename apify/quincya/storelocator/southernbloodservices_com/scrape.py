import re
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://southernbloodservices.com/contact/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    headers = {"User-Agent": user_agent}

    locator_domain = "https://southernbloodservices.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="fw-row")[1].find_all(class_="fw-text-box")
    hours = base.find_all(class_="fw-row")[3].find_all(class_="fw-text-box")
    geos = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))

    for i, item in enumerate(items):
        location_name = item.h3.text.strip()
        raw_address = list(item.stripped_strings)[1:]
        street_address = raw_address[0].replace("\xa0", " ").strip()
        city_line = raw_address[1].replace("\xa0", " ").strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = ""
        location_type = ""
        phone = raw_address[3].replace(":", "").strip()
        hours_of_operation = " ".join(list(hours[i].stripped_strings)[1:])
        latitude = geos[i].split(",")[0]
        longitude = geos[i].split(",")[1]

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
