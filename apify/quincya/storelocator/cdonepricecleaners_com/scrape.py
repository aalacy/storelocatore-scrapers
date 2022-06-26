import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.cdonepricecleaners.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location-block")
    locator_domain = "https://www.cdonepricecleaners.com/"

    for item in items:
        location_name = item.find(class_="location-block__title").text.strip()

        street_address = item.find(class_="location-block__address").span.text.strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        city_line = (
            item.find(class_="location-block__address")
            .find_all("span")[1]
            .text.strip()
            .split(",")
        )
        city = city_line[0].split("-")[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = item["id"]
        location_type = item["data-type"]
        phone = item.find(class_="location-block__phone").text.strip()
        latitude = item["data-lat"]
        longitude = item["data-lng"]

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        hours_of_operation = " ".join(
            list(base.find(class_="location-hours__list").ul.stripped_strings)
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
