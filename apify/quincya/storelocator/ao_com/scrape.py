import re


from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://ao.com/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="ao-cta-blue")
    locator_domain = "ao.com"

    for item in items:
        link = "https://ao.com" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(
                class_="details-inner text-body-sm text-secondary"
            ).p.stripped_strings
        )[2:]

        location_name = base.h2.text.strip()
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip()
        try:
            zip_code = raw_address[3].strip()
        except:
            zip_code = state
            state = "<MISSING>"

        country_code = "UK"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = " ".join(
            list(
                base.find(class_="details-inner text-body-sm text-secondary")
                .find_all("p")[1]
                .stripped_strings
            )[1:]
        )
        map_str = base.find(class_="ao-cta-blue")["href"]
        geo = re.findall(r"[0-9]{2,3}\.[0-9]+,-[0-9]{1,2}\.[0-9]+", map_str)[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]

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
