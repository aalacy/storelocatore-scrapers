from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.shell.com.au"
base_url = "https://www.shell.com.au/motorists/fuel-finder.html"
json_url = "https://data.nowwhere.com.au/v3.2/features/SHE_FuelLocations/"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=20)
        locations = json.loads(
            rr.response.body.decode("utf8")
            .split("__ng_jsonp__.__req0.finished(")[1]
            .strip()[:-2]
        )["Features"]
        for _ in locations:
            hours_of_operation = ""
            if _["status"] != "Open":
                hours_of_operation = _["status"]
            if _["open_24_hours"] == "1":
                hours_of_operation = "Open 24 Hours"
            else:
                hours = []
                for day in days:
                    day = day.lower()
                    open = f"{day}_opening"
                    close = f"{day}_closing"
                    times = "closed"
                    if _.get(open):
                        times = f"{_.get(open)} - {_.get(close)}"
                    hours.append(f"{day}: {times}")
                hours_of_operation = "; ".join(hours)
            phone = _["phone"]
            if phone == "0":
                phone = ""
            yield SgRecord(
                page_url=base_url,
                location_name=_["displayname"],
                street_address=_["street"],
                city=_["suburb"],
                state=_["state"],
                zip_postal=_.get("postcode"),
                country_code="AU",
                phone=phone,
                latitude=_["latitude"],
                longitude=_["longitude"],
                location_type=_["site_type"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
