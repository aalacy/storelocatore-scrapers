from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pfchangs.ca"
base_url = "https://pfchangs.ca/locations/"


def _p(val):
    if (
        val
        and val.replace("(", "")
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
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('$("#map1").maps(')[1]
            .split(").data(")[0]
        )["places"]
        for _ in locations:
            addr = _["location"]
            info = bs(_["content"], "lxml")
            if "Coming Soon" in info.text:
                continue

            street_address = _["address"]
            if addr["city"] in street_address:
                street_address = street_address.split(addr["city"])[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["postal_code"],
                latitude=addr["lat"],
                longitude=addr["lng"],
                country_code=addr["country"],
                phone=_p(info.a.text.strip()),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
