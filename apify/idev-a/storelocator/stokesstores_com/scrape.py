from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.stokesstores.com/"
base_url = "https://www.stokesstores.com/graphql?query=query+store_locators%7BallStores%7Bstores%7Baddress+city+contact_image+country+zipcode+store_id+code+region+name+phone+longitude+latitude+distance+bopis_enabled+is_active+is_thinkkitchen+schedule%7Bschedule_name+friday_close+friday_open+monday_close+monday_open+saturday_close+saturday_open+sunday_close+sunday_open+wednesday_open+wednesday_close+tuesday_open+tuesday_close+thursday_open+thursday_close+__typename%7D__typename%7D__typename%7D%7D&operationName=store_locators&variables=%7B%7D"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]["allStores"][
            "stores"
        ]
        for _ in locations:
            hours = []
            for day in days:
                hh = (
                    _["schedule"].get(f"{day.lower()}_open")
                    + " - "
                    + _["schedule"].get(f"{day.lower()}_close")
                )
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url="https://www.stokesstores.com/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["region"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
