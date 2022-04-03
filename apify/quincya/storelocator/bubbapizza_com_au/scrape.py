from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.bubbapizza.com.au/store-locator/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.bubbapizza.com.au"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="locatioin_list")
    for item in items:

        link = item.find_all("a")[-1]["href"]

        location_name = item.find(class_="berwick_box_tlt_new").text

        raw_data = list(item.p.stripped_strings)
        if "Centre 575" in raw_data[-1]:
            raw_data.pop(0)
        street_address = raw_data[0].replace("\t", "").split("\n")[0].strip()
        if len(raw_data) == 1:
            city_line = raw_data[0].replace("\t", "").split("\n")[1].strip().split(",")
        else:
            city_line = raw_data[-1].split(",")
        city = city_line[0]
        state = ""
        zip_code = city_line[1].strip()
        country_code = "AU"

        try:
            phone = (
                list(item.find(class_="store_add").stripped_strings)[-1]
                .split(":")[1]
                .strip()
            )
        except:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            phone = (
                list(base.find(class_="store-add").stripped_strings)[1]
                .split(":")[1]
                .strip()
            )

        store_number = ""
        location_type = "<MISSING>"
        try:
            map_link = item.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        hours_of_operation = " ".join(
            list(item.find(class_="store_tradinghour").div.stripped_strings)
        ).replace("  ", " ")

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
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
