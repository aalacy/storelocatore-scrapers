from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cafemetrony.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = (
        base.find(id="locations")
        .find(class_="dmRespColsWrapper")
        .find_all("div", recursive=False)
    )

    for item in items:
        raw_address = list(item.stripped_strings)
        location_name = raw_address[0]
        street_address = raw_address[1].split("(")[0].strip()
        city = raw_address[2].split(",")[0].strip()
        state = raw_address[2].split(",")[1].strip().split()[0]
        zip_code = raw_address[2].split(",")[1].strip().split()[1]
        country_code = "US"
        store_number = ""
        location_type = "<MISSING>"
        phone = raw_address[3]

        link = locator_domain + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = (
            " ".join(list(base.find(string="Hours").find_next().stripped_strings))
            .split("*")[0]
            .strip()
        )
        latitude = base.find(provider="mapbox")["data-lat"]
        longitude = base.find(provider="mapbox")["data-lng"]

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
