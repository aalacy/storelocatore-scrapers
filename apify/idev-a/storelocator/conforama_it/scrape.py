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

locator_domain = "https://www.conforama.it"
base_url = "https://www.conforama.it/locations"

black_list = [
    "Affi",
    "Trezzano sul Naviglio",
    "Belpasso",
    "Campogalliano",
    "Castel Mella",
    "Cittaducale",
    "Martignacco",
    "Melilli",
    "Mestre",
    "Riposto",
    "S. Sperate",
    "Settimo Torinese",
    "Tortona",
    "Trezzano sul Naviglio",
    "Veggiano",
    "Vergiate",
]


def _hoo(blocks, name):
    for loc in blocks:
        if loc.select_one("div.amlocator-title").text == name:
            return loc.select_one("div.amlocator-description").text.strip()


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("jsonLocations:")[1]
            .split("imageLocations")[0]
            .strip()[:-1]
        )
        blocks = bs(locations["block"], "lxml").select(
            "div.amlocator-store-information"
        )
        for _ in locations["items"]:
            info = bs(_["popup_html"], "lxml")
            block = list(info.stripped_strings)[1:]
            street_address = block[0]
            location_name = info.h3.text.strip()
            city = location_name.split("(")[0].strip()
            if city in black_list:
                city = ""

            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="IT",
                phone=block[2].replace(":", ""),
                hours_of_operation=_hoo(blocks, location_name),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
