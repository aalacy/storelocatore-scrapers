import re
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://scriveneroil.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://scriveneroil.com/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.table.find_all("tr")

    for item in items:
        try:
            raw_address = list(item.td.stripped_strings)
            if "(" in raw_address[1]:
                raw_address.pop(1)
        except:
            continue
        location_name = raw_address[0]
        street_address = raw_address[1].split(" Baton")[0].split("(")[0].strip()
        city_line = raw_address[2].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        try:
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            zip_code = ""
        country_code = "US"
        location_type = ""
        phone = raw_address[-1]
        if "," in phone:
            phone = ""
        store_number = ""
        hours_of_operation = ""

        try:
            map_link = item.find_all("td")[1].iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

            if not zip_code:
                req = session.get(map_link, headers=headers)
                map_str = BeautifulSoup(req.text, "lxml")
                zip_code = re.findall(r", [A-Z]{2} [0-9]{5}", str(map_str))[0][-5:]
        except:
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
    fetch_data(writer)
