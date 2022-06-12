from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://stonebridgeseniorliving.com"
base_url = "https://stonebridgeseniorliving.com/wp-json/stonebridge/v1/locations"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["location"]:
            addr = _["address"]["address"].split(",")
            yield SgRecord(
                page_url=_["permalink"],
                location_name=_["title"],
                street_address=addr[0].strip(),
                city=addr[1].strip(),
                state=_["state"],
                zip_postal=addr[2].strip().split(" ")[-1].strip(),
                latitude=_["address"]["lat"],
                longitude=_["address"]["lng"],
                country_code="US",
                phone=_["phone"],
                location_type=_["care_type"],
                locator_domain=locator_domain,
                raw_address=_["address"]["address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
