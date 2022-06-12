import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://muttsandco.com/pages/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = (
        base.find(class_="nav-bar__linklist list--unstyled")
        .find(string="Locations")
        .find_next("ul")
        .find_all("a")
    )
    locator_domain = "muttsandco.com"

    for item in items:
        link = "https://muttsandco.com" + item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "Mutts & Co - " + base.h1.text.strip()

        raw_address = (
            base.find(style="font-size: 16px; font-family: Poppins;")
            .text.replace("City OH", "City, OH")
            .split(",")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip().split()[0].strip()
        zip_code = raw_address[2].strip().split()[1].strip()

        country_code = "US"
        store_number = "<MISSING>"

        location_type = (
            base.find(string="SERVICES")
            .find_next("p")
            .text.replace("Services", "")
            .strip()
            .replace("\n\n\n", ",")
            .replace("\n", "")
            .replace(" •", ",")
        )
        location_type = (re.sub(" +", " ", location_type)).strip()
        try:
            phone = (
                base.find(style="font-size: 16px; font-family: Poppins;")
                .find_next("div")
                .text.strip()
            )
        except:
            phone = "<MISSING>"

        hours_of_operation = (
            base.find_all(class_="shg-rich-text shg-theme-text-content")[-1]
            .ul.text.replace("\n", " ")
            .strip()
        )

        latitude = re.findall(r'data-latitude="[0-9]{2}\.[0-9]+', str(base))[0].split(
            '"'
        )[1]
        longitude = re.findall(r'data-longitude="-[0-9]{2}\.[0-9]+', str(base))[
            0
        ].split('"')[1]

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
