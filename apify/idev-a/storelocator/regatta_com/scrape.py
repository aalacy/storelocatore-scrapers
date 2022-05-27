from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgzip.dynamic import DynamicGeoSearch
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.regatta.com/"
base_url = "https://backend-regatta-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1={}&lng1={}&lat2={}&lng2={}"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data(search):
    for lat, lng in search:
        with SgRequests() as session:
            import pdb

            pdb.set_trace()
            locations = session.get(
                base_url.format(lat, lng, -lat, -lng), headers=_headers
            ).json()["result"]["hits"]["hits"]
            logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
            for loc in locations:
                _ = loc["_source"]
                if "Coming Soon" in _["telephone"]:
                    continue
                street_address = _["street"]
                if _["street_line_2"]:
                    street_address += " " + _["street_line_2"]

                hours = []
                hh = json.loads(_["opening_hours"])
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                    day = day.lower()
                    start = hh.get(f"{day}_from")
                    end = hh.get(f"{day}_to")
                    hours.append(f"{day}: {start} - {end}")

                raw_address = f"{street_address} {_['city']} {_['region']} {_['postcode']} {_['country']}".replace(
                    ",", ""
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2

                search.found_location_at(_["location"]["lat"], _["location"]["lon"])
                yield SgRecord(
                    page_url="https://www.regatta.com/us/store-locator/",
                    store_number=_["store_id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_["location"]["lat"],
                    longitude=_["location"]["lon"],
                    country_code=_["country"],
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE}),
            duplicate_streak_failure_factor=50,
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=["gb"], expected_search_radius_miles=100
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
