from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.saskliquor.com"
base_url = "https://www.saskliquor.com/locations/"


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("page.locations =")[1]
            .split("page.location =")[0]
            .strip()[:-1]
        )
        for _ in locations:
            street_address = _["Address"]
            if _["Address2"]:
                street_address += " " + _["Address2"]
            hours = []
            for hh in _["HoursOfOperation"]:
                times = f"{_time(hh['Open'])}-{_time(hh['Close'])}"
                if hh["Close"] == 0:
                    times = "Closed"
                hours.append(f"{hh['DayOfWeek']}: {times}")
            page_url = (
                f"https://www.saskliquor.com/locations/{_['LocationId']}/{_['Name']}/"
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["LocationId"],
                location_name=_["DisplayName"],
                street_address=street_address,
                city=_["City"],
                state=_["ProvinceAbbrev"],
                zip_postal=_["PostalCode"],
                latitude=_["Position"]["Latitude"],
                longitude=_["Position"]["Longitude"],
                country_code="US",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
