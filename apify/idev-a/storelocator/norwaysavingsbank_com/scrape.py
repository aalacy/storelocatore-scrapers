from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.norwaysavings.bank/"
base_url = "https://www.norwaysavings.bank/wp-admin/admin-ajax.php?action=store_search&lat=44.21396&lng=-70.54481&max_results=100&search_radius=100&autoload=1"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as session:
        items = session.get(base_url, headers=_headers).json()
        for item in items:
            page_url = item["permalink"]
            location_name = (
                item["store"].replace("<strong>", "").replace("</strong>", "")
            )
            street_address = item["address"]
            if item["address2"]:
                street_address += " " + item["address2"]

            hours = list(bs(item["location_lobby_hours"], "lxml").stripped_strings)
            if hours and "temporarily closed" in hours[0].lower():
                hours = ["temporarily closed"]
            if hours and "lobby" in hours[0].lower():
                del hours[0]
            yield SgRecord(
                page_url=page_url,
                store_number=item["id"],
                location_name=location_name,
                street_address=street_address,
                city=item["city"],
                state=item["state"],
                zip_postal=item["zip"],
                latitude=item["lat"],
                longitude=item["lng"],
                country_code=item["country"],
                phone=item.get("phone", ""),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-").replace("\n", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
