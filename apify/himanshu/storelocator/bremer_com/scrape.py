from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    r = session.get(
        "https://web-api.bremer.com/v1/places?coordinates[latitude]=45.4651346&coordinates[longitude]=-94.2515552&radius=2000&operator=bremer&branch=true",
        headers=headers,
    )
    data = r.json()["bremer"]
    for store_data in data:
        hours_of_operation = ""
        raw_hours = store_data["branch_features"]["hours"]["lobbyHours"]
        for day in raw_hours:
            try:
                hours = raw_hours[day][0]["open"] + "-" + raw_hours[day][0]["close"]
            except:
                hours = "Closed"
            hours_of_operation = (hours_of_operation + " " + day + " " + hours).strip()
        link = "https://www.bremer.com/locations/" + store_data[
            "title"
        ].lower().replace(" ", "-")

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.bremer.com",
                page_url=link,
                location_name=store_data["title"],
                street_address=store_data["address"]["address1"],
                city=store_data["address"]["city"],
                state=store_data["address"]["state"],
                zip_postal=store_data["address"]["zip"],
                country_code="US",
                store_number=store_data["branch_features"]["id"],
                phone=store_data["branch_features"]["phoneLobby"],
                location_type="",
                latitude=store_data["coordinates"]["latitude"],
                longitude=store_data["coordinates"]["longitude"],
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
