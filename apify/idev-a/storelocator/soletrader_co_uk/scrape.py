from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.soletrader.co.uk"
base_url = "https://www.soletrader.co.uk/ajax/store-locator/?searchText=&pagesize=1000&pageNumber={}"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            data = session.get(base_url.format(page), headers=_headers).json()
            if data["pagination"]["hasNextPage"]:
                page += 1
            for _ in data["results"]:
                hours = []
                for x, day in enumerate(days):
                    for hh in _.get("inventoryLocationOpenHours", []):
                        if hh["day"] == x:
                            hours.append(f"{day}: {hh['openTime']} - {hh['closeTime']}")
                page_url = locator_domain + _["url"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["address2"],
                    city=_["city"],
                    state=_.get("region"),
                    zip_postal=_["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_.get("phoneNumber"),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

            if not data["pagination"]["hasNextPage"]:
                break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
