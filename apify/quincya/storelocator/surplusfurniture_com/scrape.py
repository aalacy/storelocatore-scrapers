import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.surplusfurniture.com/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(
        "div", class_=re.compile(r".+mgz-element mgz-child mgz-element-text")
    )
    locator_domain = "https://www.surplusfurniture.com"

    for item in items:
        if len(item.text) < 20:
            continue
        link = locator_domain + item.a["href"].replace("dartmouth", "halifax")
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        raw_data = list(item.stripped_strings)
        street_address = raw_data[1].strip()
        city_line = raw_data[2].replace("\xa0", " ").strip().split(",")
        city = city_line[0].strip()
        state = city_line[1].split()[0].strip()
        zip_code = " ".join(city_line[1].split()[1:]).strip()
        country_code = "CA"
        location_type = ""
        store_number = ""
        phone = (
            base.find(class_="mgz-icon-list-item-icon fas mgz-fa-phone")
            .find_next()
            .text.strip()
        )
        try:
            hours_of_operation = base.find(class_="times").get_text(" ")
        except:
            hours_of_operation = (
                base.find(class_="mgz-icon-list-item-icon far mgz-fa-clock")
                .find_next()
                .get_text(" ")
            )
        try:
            latitude = (
                re.findall(r'latitude":[0-9]{2}\.[0-9]+', str(base))[0]
                .split(":")[1]
                .strip()
            )
            longitude = (
                re.findall(r'longitude":-[0-9]{2,3}\.[0-9]+', str(base))[0]
                .split(":")[1]
                .strip()
            )
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
