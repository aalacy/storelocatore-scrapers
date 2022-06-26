import json

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

    locator_domain = "checkngo.com"

    base_link = "https://www.checkngo.com/service/location/getlocationsnear?latitude=40.8145&longitude=-96.7009&radius=10000&brandFilter=Check%20`n%20Go"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.text.strip())

    for store in stores:
        location_name = store["ColloquialName"]
        street_address = (store["Address1"] + " " + store["Address2"]).strip()
        city = store["City"]
        state = store["State"]["Code"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["StoreNum"]
        location_type = "<MISSING>"
        phone = store["FormattedPhone"]

        if not store["MondayOpen"]:
            mon = "Closed"
        else:
            mon = store["MondayOpen"] + "-" + store["MondayClose"]

        if not store["TuesdayOpen"]:
            tue = "Closed"
        else:
            tue = store["TuesdayOpen"] + "-" + store["TuesdayClose"]

        if not store["WednesdayOpen"]:
            wed = "Closed"
        else:
            wed = store["WednesdayOpen"] + "-" + store["WednesdayClose"]

        if not store["ThursdayOpen"]:
            thu = "Closed"
        else:
            thu = store["ThursdayOpen"] + "-" + store["ThursdayClose"]

        if not store["FridayOpen"]:
            fri = "Closed"
        else:
            fri = store["FridayOpen"] + "-" + store["FridayClose"]

        hours_of_operation = (
            "Monday "
            + mon
            + " Tuesday "
            + tue
            + " Wednesday "
            + wed
            + " Thursday "
            + thu
            + " Friday "
            + fri
        ).strip()

        try:
            sat = " Saturday " + store["SaturdayOpen"] + "-" + store["SaturdayClose"]
        except:
            sat = " Saturday INACCESSIBLE"
        try:
            sun = " Sunday " + store["SundayOpen"] + "-" + store["SundayClose"]
        except:
            sun = " Sunday INACCESSIBLE"

        hours_of_operation = hours_of_operation + sat + sun

        latitude = store["Latitude"]
        if latitude == 33.2:
            latitude = "33.2000"
        longitude = store["Longitude"]
        link = "https://locations.checkngo.com/locations" + store["Url"]

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
