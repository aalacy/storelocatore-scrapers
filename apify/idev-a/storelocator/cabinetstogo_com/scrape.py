from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://cabinetstogo.com"
    base_url = "https://cdn.shopify.com/s/files/1/0196/2351/0078/t/5/assets/showroomsDatabase.js?v=2326635833144775162"
    with SgRequests() as session:
        locations = demjson.decode(
            session.get(base_url, headers=_headers)
            .text.split("var stores =")[1]
            .strip()[:-1]
        )
        for _ in locations:
            if "COMING SOON" in _["showroom"]:
                continue
            hours = list(bs(_["hours"], "lxml").stripped_strings)
            if "Please contact store" in hours[0]:
                del hours[0]
            page_url = locator_domain + _["storelink"]
            phone = _["phone"]
            if "not available" in phone:
                phone = ""
            hours_of_operation = "; ".join(hours)
            if "not available" in hours_of_operation:
                hours_of_operation = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_["showroom"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                latitude=_["lat"],
                longitude=_["lon"],
                phone=phone,
                zip_postal=_["zip"],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
