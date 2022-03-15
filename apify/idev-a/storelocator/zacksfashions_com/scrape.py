from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://cazzapetitezacks.com"
base_url = "https://stockist.co/api/v1/u6281/locations/all.js?callback=_stockistAllStoresCallback"
page_url = "https://cazzapetitezacks.com/pages/store-locator"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("_stockistAllStoresCallback(")[1]
            .strip()[:-2]
        )
        for _ in locations:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            phone = _["phone"].split(":")[-1].replace(",", "").strip()
            if not _p(phone):
                phone = ""
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
