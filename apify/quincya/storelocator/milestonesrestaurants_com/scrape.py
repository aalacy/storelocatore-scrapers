from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://milestonesrestaurants.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "milestonesrestaurants.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("a", class_="awb-custom-text-color")
    for item in items:
        link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h4.text

        raw_data = list(base.find(class_="fusion-text fusion-text-1").stripped_strings)
        street_address = raw_data[0]
        city_line = raw_data[1].replace(",", "").split()
        city = " ".join(city_line[:-3])
        state = city_line[-3]
        zip_code = " ".join(city_line[-2:])
        country_code = "CA"
        phone = base.h6.text
        store_number = base.find(id="content").div["id"].split("-")[1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = ""

        tables = base.find_all(class_="fusion-builder-row")
        for table in tables:
            if "hours" in table.text.lower():
                raw_hours = list(table.stripped_strings)[1:]
                if "day" not in raw_hours[0]:
                    raw_hours.pop(0)
                hours_of_operation = (
                    " ".join(raw_hours).split("Brunch")[0].split("Happy")[0].strip()
                )
                if hours_of_operation[-1:] == "-":
                    hours_of_operation = hours_of_operation[:-1].strip()
                break

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
