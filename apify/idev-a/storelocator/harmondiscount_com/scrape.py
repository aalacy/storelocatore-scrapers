from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgzip.dynamic import SearchableCountries, DynamicZipSearch, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("golden1")

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
}

locator_domain = "https://www.harmonfacevalues.com"
base_url = "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%22{}%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2230%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%22100%22,%22maxMatches%22:20,%22ambiguities%22:%22ignore%22,%22units%22:%22m%22%7D%7D"


def fetch_records(http: SgRequests, search: DynamicZipSearch) -> Iterable[SgRecord]:
    for zip in search:
        locations = (
            http.get(base_url.format(zip), headers=_headers)
            .json()
            .get("searchResults", [])
        )
        logger.info(f"[{zip}] {len(locations)} found")
        for loc in locations:
            _ = loc["fields"]
            yield SgRecord(
                page_url="https://www.harmonfacevalues.com/store/selfservice/FindStore",
                location_name=loc["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["Lat"],
                longitude=_["Lng"],
                phone=_["Phone"],
                country_code=_["country"],
                locator_domain=locator_domain,
                hours_of_operation=_["hours"].replace(",", ";"),
            )


if __name__ == "__main__":
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
