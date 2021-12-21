from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
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

locator_domain = "https://es.littlecaesars.com"
base_url = "https://es.littlecaesars.com/es-es/contacto/"
json_url = "https://es.littlecaesars.com/component---src-pages-contacto-tsx"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url)
        locations = json.loads(
            rr.response.body.decode()
            .split("t.exports=JSON.parse('")[1]
            .split("')},I6tc")[0]
        )["data"]["allDatoCmsFranchiseeLocationList"]["nodes"]
        for loc in locations:
            default_hours = [hh["line"] for hh in loc["defaultHours"]]
            for _ in loc["locationList"]:
                raw_address = [aa["line"] for aa in _["address"]]
                hours = [hh["line"] for hh in _["hours"]]
                if not hours:
                    hours = default_hours
                addr = parse_address_intl(" ".join(raw_address) + ", Spain")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="Spain",
                    phone=_["telephoneNumber"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(raw_address),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
