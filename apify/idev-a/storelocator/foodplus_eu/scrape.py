from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.foodplus.eu"
base_url = "https://www.foodplus.eu/includes/stores.php?lang=en"

types = {
    "1": "Alcohol",
    "2": "ATM",
    "3": "Cashback",
    "4": "Food to go / Takeaway",
    "5": "Card Payments",
    "6": "Air conditioning",
    "7": "Lotto/ The National Lottery",
    "8": "Beer",
    "9": "Shipments",
    "10": "Fresh meat",
    "11": "Cash transfer",
}


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("marker")
        for _ in locations:
            hours = []
            for hh in bs(_["open_hours"], "lxml").select("div.row.open-hours"):
                hours.append(
                    f"{hh.select_one('div.days').text.strip()} {hh.select('div.col')[1].text.strip()}"
                )
            page_url = f"https://www.foodplus.eu/en/map/{_['slug']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["zip_code"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                location_type=types[_["store_type_id"]],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
