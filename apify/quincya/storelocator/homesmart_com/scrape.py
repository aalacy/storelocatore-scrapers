from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://homesmart.com/offices-agents-search/?cmd=search"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    payload = {"officeSearch": "a", "state": "ALL", "officeCity": "ALL", "button": ""}

    session = SgRequests()
    response = session.post(base_link, headers=headers, data=payload)
    base = BeautifulSoup(response.text, "lxml")

    items = base.find_all(id="office-result")
    locator_domain = "homesmart.com"

    for item in items:
        location_name = item.h3.text.strip()
        raw_address = list(item.find(class_="address").stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[-1].split(",")
        city = city_line[0].strip()
        state = city_line[1][:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = item.find_all("p")[1].text.split(":")[1].strip()
            if not phone:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        link = (
            "https://homesmart.com/officesagents/?"
            + item.find(id="agents")["href"].split("?")[-1].strip()
        ).replace(" ", "%20")

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
