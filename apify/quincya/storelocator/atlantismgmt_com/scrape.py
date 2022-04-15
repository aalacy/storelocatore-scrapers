from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.atlantismgmt.com/map-locations/?mpfy-pin=1236"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "atlantismgmt.com"

    items = base.find_all(class_="mpfy-mll-location")
    for item in items:
        location_name = (
            item.find(class_="mpfy-mll-l-title").span.text.split("(")[0].strip()
        )
        raw_address = item.find(class_="mpfy-mll-l-content").p.text.split("|")
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].strip()
        zip_code = city_line[2].strip()
        country_code = "US"
        phone = ""
        store_number = item["data-id"]
        location_type = ""
        hours_of_operation = ""

        map_link = (
            item.find(class_="mpfy-mll-l-buttons")
            .find_all("a")[-1]["href"]
            .split("=")[-1]
        )
        latitude = map_link.split(",")[0].strip()
        longitude = map_link.split(",")[1].strip()

        if str(latitude) == "0":
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
