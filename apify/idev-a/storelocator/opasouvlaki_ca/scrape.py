from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
import us

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://opasouvlaki.ca"
base_url = (
    "https://opasouvlaki.ca/wp-json/opasouvlaki/v1/nearest-locations/37.751/-97.822"
)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ca_provinces = [
    "alberta",
    "british columbia",
    "manitoba",
    "new brunswick",
    "newfoundland and labrador",
    "nova scotia",
    "ontario",
    "prince edward island",
    "quebec",
    "saskatchewan",
]
ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            raw_address = _.get("googleaddress")
            if not raw_address:
                raw_address = _.get("address")
            hours = []
            for day in days:
                hh = _.get(day.lower())
                if _.get(day.lower()):
                    try:
                        times = f"{hh['open']} - {hh['close']}"
                    except:
                        times = "closed"
                    hours.append(f"{day}: {times}")
            addr = parse_address_intl(raw_address)
            state = _.get("province")
            zip_postal = addr.postcode
            if not state:
                state = addr.state
            country_code = "CA"
            if state:
                if us.states.lookup(state):
                    country_code = "US"
                elif (
                    state.lower() in ca_provinces_codes or state.lower() in ca_provinces
                ):
                    country_code = "CA"
            if zip_postal and zip_postal.isdigit():
                country_code = "US"
            yield SgRecord(
                page_url="https://opasouvlaki.ca/locations/?updateLocation=1",
                store_number=_["id"],
                location_name=_["location"],
                street_address=_["address"],
                city=_["city"],
                state=state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=country_code,
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
