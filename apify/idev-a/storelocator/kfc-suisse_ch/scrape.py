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

locator_domain = "https://www.kfc-suisse.ch"
base_url = "https://www.kfc-suisse.ch/restaurants/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var restaurants =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        for _ in locations:
            city = bs(_["city"], "lxml")
            hours = []
            temp = []
            for hh in bs(_["openingHours"], "lxml").stripped_strings:
                if "Dine" in hh or "Take" in hh:
                    continue
                if "Delivery" in hh:
                    break
                temp.append(hh)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            yield SgRecord(
                page_url="https://www.kfc-suisse.ch/restaurants/",
                store_number=_["uid"],
                location_name=_["title"],
                street_address=_["street"].replace("&#039;", "'"),
                city=city.select_one(".city").text.strip(),
                zip_postal=city.select_one(".zip").text.strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Switzerland",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
