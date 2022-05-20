import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.immunotek.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "immunotek.com"

    items = base.find_all(class_="location_entry")
    for i in items:

        location_name = "ImmunoTek " + i.find(class_="location_title").text
        if "*" in location_name:
            continue

        link = i.a["href"]
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        raw_address = list(item.find(class_="address").stripped_strings)
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        zip_code = raw_address[1].split(",")[1].split()[1]
        country_code = "US"
        store_number = item.article["id"].split("-")[1]
        location_type = "<MISSING>"
        phone = item.find("a", {"href": re.compile(r"tel:")}).text
        latitude = item.find(class_="marker")["data-lat"]
        longitude = item.find(class_="marker")["data-lng"]
        hours_of_operation = " ".join(list(item.find(class_="hours").stripped_strings))

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
