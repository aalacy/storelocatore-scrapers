from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.villagemedical.com"
base_url = "https://www.villagemedical.com/locator"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split("locations[")[1:]
        for loc in locations:
            try:
                _ = json.loads(loc.split(" = ")[1])["location"]
            except:
                break
            addr = _["address"]
            street_address = addr["street"]
            if addr.get("street_2"):
                street_address += " " + addr["street_2"]
            page_url = locator_domain + _["url"]
            hours = []
            for day, hh in _.get("hours", {}).items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"].replace("–", "-"),
                street_address=street_address,
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zip"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
