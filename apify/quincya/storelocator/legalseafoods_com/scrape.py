from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.legalseafoods.com/locations-menus/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="jet-listing-grid__item custom locationItem")
    locator_domain = "legalseafoods.com"

    for item in items:

        location_name = item.a.get_text(" ").split("-")[0].strip()
        raw_address = list(item.section.stripped_strings)
        if raw_address[0] == "Temporarily Closed":
            raw_address.pop(0)
        street_address = raw_address[0].replace("Assembly Row,", "").strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address[2].strip()

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if (
            "Temporarily Closed" in item.text
            or "This location is Temporarily Closed" in base.text
        ):
            street_address = street_address.replace("Temporarily Closed -", "").strip()
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                hours_of_operation = (
                    " ".join(list(base.table.stripped_strings)[1:])
                    .split("See About")[0]
                    .strip()
                )
            except:
                hours_of_operation = "<MISSING>"
        try:
            map_link = base.find_all("iframe")[-1]["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
