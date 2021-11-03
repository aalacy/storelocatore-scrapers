from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://7-eleven.se"
base_url = "https://7-eleven.se/hitta-butik/"
json_url = "/storage/v1/b/new-rcs-web-711-prod.appspot.com/o/stores.json"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        request = driver.wait_for_request(json_url, timeout=50)
        locations = json.loads(request.response.body)
        for _ in locations:
            hours = []
            for hh in _.get("openhours", {}).get("standard", []):
                hours.append(f"{days[hh['weekday']]}: {' - '.join(hh['hours'])}")
            yield SgRecord(
                page_url="https://7-eleven.se/hitta-butik/",
                store_number=_["storeId"],
                location_name=_["title"],
                street_address=" ".join(_["address"]),
                city=_["city"],
                state=_.get("county"),
                zip_postal=_.get("postalCode"),
                latitude=_["location"]["lat"],
                longitude=_["location"]["lng"],
                country_code="Sweden",
                phone=_["phone"],
                location_type=_["locationType"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
