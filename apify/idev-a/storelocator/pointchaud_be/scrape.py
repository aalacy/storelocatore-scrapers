from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pointchaud.be"
base_url = "https://www.pointchaud.be/fr/Trouver-un-point-chaud"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            "{"
            + session.get(base_url, headers=_headers)
            .text.split("window.networkMap = {")[1]
            .split("window.services")[0]
            .strip()[:-1]
        )["markers"]
        for _ in locations:
            addr = _["article_infos"]
            raw_address = _["address"]
            hours = []
            if addr["openings"]:
                hours.append(f"Monday to Friday: {addr['openings'].strip()}")
            if addr.get("saterday"):
                hours.append(f"Saturday: {addr['saterday'].strip()}")
            if addr.get("sunday"):
                hours.append(f"Sunday: {addr['sunday'].strip()}")

            _addr = raw_address.split(",")
            hours_of_operation = "; ".join(hours)
            if hours_of_operation.endswith(","):
                hours_of_operation = hours_of_operation[:-1]
            yield SgRecord(
                page_url=addr["link"] or base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=_addr[0],
                city=addr["town"],
                zip_postal=addr["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="BE",
                phone=addr["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
