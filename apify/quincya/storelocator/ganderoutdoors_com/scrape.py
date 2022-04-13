from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.ganderrv.com/state-directory"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location_name")
    locator_domain = "https://www.ganderrv.com"

    for item in items:
        if "gander" in item.text.lower():
            link = locator_domain + item["href"].strip().replace(" ", "%20")

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = base.h1.text.strip()
            if "gander" not in location_name.lower():
                continue

            raw_address = list(base.find(class_="col address").p.stripped_strings)
            street_address = raw_address[0].strip()
            city_line = raw_address[-1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = ""

            location_type = ""
            phone = base.find(class_="phone-number").text.strip()
            hours_of_operation = " ".join(
                list(base.find(class_="storehours").stripped_strings)[1:-1]
            )

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
