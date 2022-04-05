import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://local.checkintocash.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://checkintocash.com/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="fl-content col-md-12").find_all("a")
    for item in items:

        link = item["href"]
        if link.count("/") < 5:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text
        raw_address = base.find(attrs={"itemprop": "streetAddress"}).text.split(",")
        street_address = " ".join(raw_address[:-3]).replace("  ", " ").strip()
        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        country_code = "US"
        phone = base.find(attrs={"itemprop": "telephone"}).text.strip()

        store_number = ""
        location_type = ""
        hours_of_operation = ""

        try:
            hours_of_operation = " ".join(
                list(base.find(id="openIntervals").stripped_strings)
            )
        except:
            try:
                if (
                    "store is closed"
                    in base.find(class_="rate-state-table").text.lower()
                ):
                    hours_of_operation = "Temporarily Closed"
            except:
                pass

        latitude = ""
        longitude = ""

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
