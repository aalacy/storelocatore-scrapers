from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return val.replace("-", "").replace(".", "").strip()


def fetch_data():
    locator_domain = "http://realfruitbubbletea.com/"
    base_url = "http://realfruitbubbletea.com/location/index.php"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("data = ")[1].split("var html")[0].strip()[:-1]
        )
        for _ in locations:
            hours = []
            hours.append(f"Mon: {_['w0']}")
            hours.append(f"Tue: {_['w1']}")
            hours.append(f"Wed: {_['w2']}")
            hours.append(f"Thu: {_['w3']}")
            hours.append(f"Fri: {_['w4']}")
            hours.append(f"Sat: {_['w5']}")
            hours.append(f"Sun: {_['w6']}")
            phone = _["phone"]
            if not _phone(phone):
                phone = ""
            addr = parse_address_intl(_["address"])
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["place"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=_["state"],
                zip_postal=addr.postcode,
                latitude=_["geo_lat"],
                longitude=_["geo_lon"],
                country_code=addr.country,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
