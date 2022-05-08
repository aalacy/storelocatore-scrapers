from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bowtiecinemas.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="c-dropdown__menu c-dropdown__menu--columns").find_all("a")

    for item in items:
        link = locator_domain + item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.find(class_="c-theater-header__name").text.strip()
        raw_address = (
            base.find(class_="c-theater-header__address").text.strip().split(",")
        )
        street_address = (
            " ".join(raw_address[0].split()[:-1]).replace("Saratoga", "").strip()
        )
        city_line = raw_address[1].split(",")
        city = raw_address[0].split()[-1].replace("Springs", "Saratoga Springs")
        state = raw_address[1].split()[0]
        zip_code = raw_address[1].split()[1]
        if "Street South" in street_address:
            street_address = street_address.replace("South", "").strip()
            city = "South " + city
        country_code = "US"
        store_number = ""
        location_type = "CINEMA"
        if "amc" in item["class"][-1]:
            location_type = "AMC"
        phone = base.find_all(class_="c-theater-header__address")[-1].text.strip()
        hours_of_operation = ""
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
