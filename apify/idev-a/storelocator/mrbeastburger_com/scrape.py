from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from datetime import datetime, timedelta

logger = SgLogSetup().get_logger("quizclothing")
_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-device-id": "1d605e0d-84ed-493a-98d2-fa501440775f",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mrbeastburger.com"
base_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants?includePrivate=false&calendarstart=20211213&calendarend=20211220"
calendar_url = "https://api.dineengine.io/mrbeastburger/custom/dineengine/vendor/olo/restaurants/{}/calendars?from={}&to={}"
today = datetime.today()
mon = (today + timedelta(days=-today.weekday())).strftime("%Y%m%d")
next_mon = (today + timedelta(days=-today.weekday(), weeks=1)).strftime("%Y%m%d")


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["restaurants"]
        for _ in locations:
            page_url = locator_domain + "/locations" + _["url"].split("/menu")[-1]
            logger.info(page_url)
            ca = session.get(
                calendar_url.format(_["id"], mon, next_mon), headers=_headers
            ).json()["calendar"]
            hours = []
            for hr in ca:
                if not hr["label"]:
                    for hh in hr["ranges"]:
                        hours.append(
                            f"{hh['weekday']}: {hh['start'].split()[-1]} - {hh['end'].split()[-1]}"
                        )
                    break
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetaddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
