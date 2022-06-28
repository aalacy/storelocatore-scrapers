from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}
    session = SgRequests()

    locator_domain = "https://www.unitedcarpetsandbeds.com"

    for page in range(1, 25):
        base_link = f"https://www.unitedcarpetsandbeds.com/amlocator/index/ajax/?p={page}?lat=0&lng=0&radius=0&product=0&category=0&sortByDistance=false"
        stores = session.get(base_link, headers=headers).json()["items"]

        for store in stores:
            raw_data = BeautifulSoup(store["popup_html"], "lxml")
            location_name = raw_data.a["title"]
            street_address = (
                list(raw_data.stripped_strings)[1].replace("Address:", "").strip()
            ).split("(")[0]
            city = list(raw_data.stripped_strings)[2].replace("City:", "").strip()
            state = ""
            zip_code = (
                list(raw_data.stripped_strings)[3].replace("Postcode:", "").strip()
            )
            country_code = "GB"
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = raw_data.find(class_="fa fa-phone").find_previous().text.strip()
            latitude = store["lat"]
            longitude = store["lng"]

            link = raw_data.a["href"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            hours_of_operation = " ".join(
                list(base.find(class_="amlocator-schedule-table").stripped_strings)
            )

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
