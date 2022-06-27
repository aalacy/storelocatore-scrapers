from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://tumbles.net/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location-item flex")

    for item in items:
        if "coming soon" in item.text.lower():
            continue
        location_name = item.h3.text
        raw_address = list(item.p.stripped_strings)
        try:
            if "Upstairs" in raw_address[1]:
                raw_address.pop(1)
        except:
            pass
        street_address = raw_address[0].split(" Baton")[0].split("(")[0].strip()
        try:
            city_line = raw_address[1].split(",")
        except:
            city_line = raw_address[0].split(" A-10")[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        phone = item.a.text
        store_number = ""
        hours_of_operation = ""
        link = item.find(class_="btn-wrap").a["href"]
        try:
            map_link = item.find(class_="img-wrap").a["href"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = ""
            longitude = ""

        sgw.write_row(
            SgRecord(
                locator_domain="https://tumbles.net/",
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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
