from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-ca:{}@proxy.apify.com:8000/"

logger = SgLogSetup().get_logger("")

locator_domain = "http://www.kfc.hr"
base_url = "https://kfc.hr/en/restaurants"
json_url = "https://api.amrest.eu/amdv/ordering-api/KFC_HR/rest/v2/restaurants/"
detail_url = (
    "https://api.amrest.eu/amdv/ordering-api/KFC_HR/rest/v2/restaurants/details/{}"
)
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as http:
        with SgChrome(block_third_parties=True) as driver:
            driver.get(base_url)
            rr = driver.wait_for_request(json_url, timeout=30)
            locations = http.get(rr.url, headers=dict(rr.headers)).json()["restaurants"]
            for loc in locations:
                url = detail_url.format(loc["id"])
                logger.info(url)
                _ = http.get(url, headers=dict(rr.headers)).json()["details"]

                street_address = _["addressStreet"]
                if _["addressStreetNo"]:
                    street_address += " " + _["addressStreetNo"]
                hours = []
                if loc["twentyFourHoursOpen"]:
                    hours = ["24 hours"]
                elif _.get("facilityOpenHours"):
                    fac = _.get("facilityOpenHours")
                    for day in days:
                        _day24 = f"open{day}24h"
                        _day = f"openHours{day}"
                        if fac[_day24]:
                            hours.append(f"{day}: 24 hours")
                        elif fac.get(_day):
                            times = []
                            for hr in fac[_day]:
                                times.append(f"{hr['openFrom']} - {hr['openTo']}")
                            hours.append(f"{day}: {', '.join(times)}")

                yield SgRecord(
                    page_url=base_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["addressCity"],
                    zip_postal=_["addressPostalCode"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    phone=_.get("phoneNo"),
                    country_code="Croatia",
                    locator_domain=locator_domain,
                    hours_of_operation=" ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
