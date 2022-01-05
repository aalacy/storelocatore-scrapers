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

locator_domain = "https://www.samedelman.com"
base_url = "https://www.samedelman.com/store-locations"
json_url = "https://platform.cloud.coveo.com/rest/search/v2"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=20)
        locations = json.loads(rr.response.body)["results"]
        for loc in locations:
            _ = loc["raw"]
            street_address = _["address1"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            hours = []
            for day in days:
                day = day.lower()
                if _.get(f"{day}hours"):
                    times = _.get(f"{day}hours")
                    hours.append(f"{day}: {times}")
            yield SgRecord(
                page_url=base_url,
                store_number=_["storeid"],
                location_name=_["title"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"].replace("0000", ""),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phonenumber"],
                location_type=_["objecttype"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
