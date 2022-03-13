from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from datetime import datetime
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("carrefour")

locator_domain = "https://www.carrefour-martinique.com/"
json_url = "/api/v1/store"
urls = {
    "Martinique": "https://www.carrefour-martinique.com/nos-magasins",
    "Guyana": "https://www.carrefour-guyane.com/nos-magasins",
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        for country, base_url in urls.items():
            logger.info(base_url)
            del driver.requests

            driver.get(base_url)
            rr = driver.wait_for_request(json_url)
            locations = json.loads(rr.response.body)["result"]
            for id, _ in locations.items():
                c_z = _["zipcode"].split()
                hours = []
                for x, _day in enumerate(days):
                    for date, hr in _["opening_hours"].items():
                        day = int(datetime.strptime(date, "%Y-%m-%d").weekday())
                        if day == x:
                            for hh in hr:
                                hours.append(
                                    f"{_day}: {hh['start_time']} - {hh['end_time']}"
                                )
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["store_code"],
                    location_name="Carrefour " + _["name"],
                    street_address=_["address"],
                    city=" ".join(c_z[1:]),
                    zip_postal=c_z[0],
                    latitude=_["latlng"]["latitude"],
                    longitude=_["latlng"]["longitude"],
                    country_code=country,
                    phone=_["store_phone"],
                    location_type="Convenience Store",
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
