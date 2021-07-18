from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    if val.endswith(","):
        val = val[:-1]
    return val.strip()


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    locator_domain = "https://www.kernelspopcorn.com/"
    base_url = "https://www.wowmobile.ca/en/locations/"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url)
            .text.split("page.locations =")[1]
            .split("page.location")[0]
            .strip()[:-1]
        )
        for _ in locations:
            street_address = _["Address"]
            if _["Address2"]:
                street_address += " " + _["Address2"]
            page_url = f'{base_url}{_["LocationId"]}/{_["Name"].replace(" ", "-")}'
            hours = []
            for hh in _["HoursOfOperation"]:
                hours.append(
                    f"{hh['DayOfWeek']}: {_time(hh['Open'])}-{_time(hh['Close'])}"
                )

            yield SgRecord(
                page_url=page_url,
                store_number=_["LocationId"],
                location_name=_["Name"],
                street_address=_valid(street_address),
                city=_["City"],
                state=_["ProvinceAbbrev"],
                zip_postal=_["PostalCode"],
                latitude=_["Google_Latitude"],
                longitude=_["Google_Longitude"],
                country_code=_["CountryCode"],
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
