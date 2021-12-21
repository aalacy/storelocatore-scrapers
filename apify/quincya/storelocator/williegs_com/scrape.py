from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.williegs.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="hero").find_all(class_="btn btn-brand")
    locator_domain = "williegs.com"

    for item in items:
        link = "https://www.williegs.com" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(base.find(id="intro").a.stripped_strings)
        street_address = raw_address[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        location_name = "Willie G’s " + city
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find("a", attrs={"data-bb-track-category": "Phone Number"}).text
        hours_of_operation = (
            base.find(id="intro")
            .p.find_next("p")
            .get_text(" ")
            .split("Happy")[0]
            .strip()
        )
        latitude = base.find(class_="gmaps")["data-gmaps-lat"]
        longitude = base.find(class_="gmaps")["data-gmaps-lng"]

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
