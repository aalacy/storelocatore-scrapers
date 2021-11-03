import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://americashloans.net/locations/locations-by-state/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="list-group-item")
    locator_domain = "americashloans.net"

    for item in items:
        link = "https://americashloans.net" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        raw_address = list(base.find(class_="location-meta-info").stripped_strings)[
            1
        ].split("\r\n")
        if len(raw_address) == 1:
            raw_address = list(base.find(class_="location-meta-info").stripped_strings)[
                1
            ].split("\n")
        street_address = raw_address[0].strip()
        city = raw_address[1].split(",")[0].strip()
        state = raw_address[1].split(",")[1].split()[0].strip()
        zip_code = raw_address[1].split(",")[1].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = base.find(class_="location-meta-info").a.text.strip()
        except:
            phone = "<MISSING>"

        raw_hours = (
            list(base.find(class_="location-meta-info").stripped_strings)[-1]
            .replace("\r\n", " ")
            .replace("\n", " ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", raw_hours)).strip()

        map_data = base.find(id="map")
        latitude = map_data["data-latitude"]
        longitude = map_data["data-longitude"]

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
