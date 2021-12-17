from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.boosterjuice.com"
base_url = "https://www.boosterjuice.com/WebServices/Booster.asmx/StoreLocations"

ca_provinces = [
    "alberta",
    "british columbia",
    "manitoba",
    "new brunswick",
    "newfoundland",
    "nova scotia",
    "ontario",
    "prince edward island",
    "quebec",
    "saskatchewan",
    "northwest territories",
    "yukon",
]

mexico_provinces = ["nuevo león"]

uae_provinces = ["emirate of dubai"]


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces:
        return "CA"
    elif code in mexico_provinces:
        return "MX"
    elif code in uae_provinces:
        return "UAE"
    else:
        return "<MISSING>"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            for hh in _["hours"]:
                if hh["isClosed"]:
                    times = "closed"
                else:
                    times = f"{hh['open']} - {hh['close']}"
                hours.append(f"{hh['day']}: {times}")
            latitude = _["latitude"]
            longitude = _["longitude"]
            if latitude == 0:
                latitude = ""
            if longitude == 0:
                longitude = ""
            page_url = f"https://www.boosterjuice.com/find-a-location/#{_['number']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["number"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["province"],
                zip_postal=_["postalCode"],
                latitude=latitude,
                longitude=longitude,
                country_code=get_country_by_code(_["province"].lower().strip()),
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
