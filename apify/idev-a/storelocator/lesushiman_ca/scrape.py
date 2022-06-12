from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Referer": "https://lesushimanorders.bon-app.ca/",
    "Origin": "https://lesushimanorders.bon-app.ca",
    "Host": "lesushimanorders.bon-app.ca",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "angular-data": '{"brandIds":[752]}',
    "lang": "en",
    "tkn": "",
    "env": "prod",
    "device-id": "16170908403832886816",
}


def fetch_data():
    locator_domain = "https://lesushimanorders.bon-app.ca/"
    base_url = "https://lesushimanorders.bon-app.ca/api/brand/brand-locations"
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, data=data).json()
        for _ in locations:
            street_address = _["AddressLine1"]
            if _["AddressLine2"]:
                street_address += ", " + _["AddressLine2"]
            yield SgRecord(
                store_number=_["Id"],
                page_url=locator_domain,
                location_name=_["Name"],
                street_address=street_address,
                city=_["City"],
                state=_.get("State", ""),
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                zip_postal=_["PostalCode"],
                country_code="US",
                phone=_["PhoneNum"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
