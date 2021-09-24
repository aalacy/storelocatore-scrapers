from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8

logger = SgLogSetup().get_logger("potbelly")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.potbelly.com"
base_url = "https://www.potbelly.com/location-finder"


def _t(val):
    return val.split()[-1]


def fetch_records(http, search):
    for lat, lng in search:
        url = f"https://api.prod.potbelly.com/v1/restaurants/nearby?lat={lat}&long={lng}&includeHours=true"
        locations = http.get(url, headers=_headers).json()["restaurants"]
        logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
        for _ in locations:
            hours = []
            if _["calendars"]:
                for hh in _["calendars"][0]["ranges"]:
                    hours.append(
                        f"{hh['weekday']}: {_t(hh['start'])} - {_t(hh['end'])}"
                    )
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=_["streetaddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["telephone"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
