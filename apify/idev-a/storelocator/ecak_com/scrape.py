from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.clarksoneyecare.com"
base_url = "https://www.clarksoneyecare.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="application/json")
            .string
        )["props"]["pageProps"]["locations"]
        for _ in locations:
            street_address = _["address1"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            if _.get("address3"):
                street_address += " " + _["address3"]
            page_url = base_url + _["slug"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipCode"],
                latitude=_["map"]["lat"],
                longitude=_["map"]["lon"],
                country_code="US",
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
