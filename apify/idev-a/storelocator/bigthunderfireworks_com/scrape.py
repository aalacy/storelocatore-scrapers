from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bigthunderfireworks.com"
base_url = "https://main-apis-prd.mapme.com/api/stories/aggregated/american-fireworks"
category = "7984a0d2-4133-4fb9-95bb-1878ded22734"


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).json()["mapmeStories"][0]
        locations = res["sections"]
        for key, _ in locations.items():
            if key not in res["categories"][category]["sections"]:
                continue
            if not _["mapView"].get("center"):
                continue
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if _.get("description"):
                info = list(bs(_["description"], "lxml").stripped_strings)
                if _p(info[-1].split(":")[-1]):
                    phone = _p(info[-1].split(":")[-1])
            yield SgRecord(
                page_url="https://viewer.mapme.com/american-fireworks/locations?categories=7984a0d2-4133-4fb9-95bb-1878ded22734",
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["mapView"]["center"]["lat"],
                longitude=_["mapView"]["center"]["lng"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
