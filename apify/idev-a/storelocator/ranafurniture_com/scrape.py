from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.ranafurniture.com/"
    base_url = "https://www.ranafurniture.com/web/services/StoreLocator.Service.ss?c=ACCT87954&latitude=40.7127753&locationtype=1&longitude=-74.0059728&n=2&page=all&radius=500000&sort=distance"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url="https://www.altamed.org/find/results?type=clinic&keywords=85281&affiliates=yes",
                store_number=_["internalid"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
