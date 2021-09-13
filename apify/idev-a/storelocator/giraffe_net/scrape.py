from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://giraffe.net"
base_url = "https://giraffe.net/find-a-giraffe"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split(":restaurants=")[1]
            .split(":footer-data")[0]
            .strip()[1:-1]
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&quot;", '"')
        )
        for _ in locations:
            page_url = locator_domain + _["url"]
            hours = []
            for hh in _["opening_hours"]:
                times = "closed"
                if not hh["restaurant_closed"]:
                    times = f"{hh['opening_time']} - {hh['closing_time']}"
                hours.append(f"{hh['day']}: {times}")
            street_address = []
            for aa in _["address"]:
                street_address.append(aa["address_line"])
            yield SgRecord(
                page_url=page_url,
                store_number=_["restaurant_id"],
                location_name=_["title"],
                street_address=" ".join(street_address).replace("&#39;", "'"),
                city=_["city"],
                state=_["county"],
                zip_postal=_["post_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
