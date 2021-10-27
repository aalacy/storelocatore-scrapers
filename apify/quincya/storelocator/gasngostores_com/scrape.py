from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://gasngostores.com/UserDashboard/GetStoreSearchList?latitude=0&longitude=0"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "gasngostores.com"

    for store in stores:
        try:
            street_address = (
                store["addressLine1"].strip()
                + " "
                + store["addressLine2"].strip()
                + " "
                + store["addressLine3"].strip()
            ).strip()
        except:
            street_address = store["addressLine1"].strip()
        city = store["cityName"]
        state = store["stateName"]
        zip_code = store["zipCode"]
        location_name = store["storeName"]
        country_code = "US"
        store_number = store["storeID"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]

        link = "https://gasngostores.com/UserDashboard/WelcomeStore/" + str(
            store_number
        )
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_type = ""
        raw_types = base.find(class_="col-md-5").find_all("li")
        for row in raw_types:
            location_type = location_type + ", " + row.text
        location_type = location_type[1:].strip()

        raw_hours = session.get(
            "https://gasngostores.com/UserDashboard/StoreDayList?StoreID="
            + str(store_number),
            headers=headers,
        ).json()
        hours_of_operation = ""
        for row in raw_hours:
            day = row["dayName"]
            opens = row["openAt"]
            closes = row["closeAt"]
            clean_hours = day + " " + opens + "-" + closes
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

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
