from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://lavidamassage.com/"
base_url = "https://lavidamassage.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=80d9aea29c&load_all=1&layout=1/"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Referer": "https://lavidamassage.com/locations/",
}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = []
            if _["description"] and "coming soon" in _["description"].lower():
                continue
            try:
                for key, value in json.loads(_["open_hours"]).items():
                    times = "Closed"
                    if value:
                        times = value[0]
                    hours.append(f"{key}: {times}")
            except:
                pass

            yield SgRecord(
                page_url="https://lavidamassage.com/locations",
                store_number=_["id"],
                location_name=_["title"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                country_code="US",
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
