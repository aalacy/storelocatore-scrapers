import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://qolhs.org/location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://qolhs.org/"

    items = base.find(class_="uc_post_list").find_all("a")

    for item in items:
        link = item["href"]
        if "/locations/" in link:
            continue
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(id="main")
            .find(class_="elementor-icon-list-items")
            .stripped_strings
        )

        location_name = base.h1.text.strip()
        street_address = raw_address[0]
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        phone = raw_address[2].split("/")[0].strip()
        store_number = ""
        map_link = base.iframe["src"]
        req = session.get(map_link, headers=headers)
        map_str = BeautifulSoup(req.text, "lxml")
        geo = (
            re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        location_type = ", ".join(
            list(base.find(id="uc_services").stripped_strings)
        ).replace(", Read More", "")
        hours_of_operation = " ".join(
            list(
                base.find(id="main")
                .find(class_="elementor-icon-list-items")
                .find_all("li")[-1]
                .stripped_strings
            )
        )

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
