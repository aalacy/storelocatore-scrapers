from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "application/json, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "order.pizzapatron.com",
    "__RequestVerificationToken": "",
    "X-Requested-With": "XMLHttpRequest",
    "X-Olo-Request": "1",
    "X-Olo-Viewport": "Desktop",
    "X-Olo-App-Platform": "web",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pizzapatron.com"
base_url = "https://order.pizzapatron.com/api/vendors/regions?excludeCities=true"


def fetch_data():
    with SgRequests() as session:
        states = session.get(base_url, headers=_headers).json()
        for state in states:
            state_url = (
                f"https://order.pizzapatron.com/api/vendors/search/{state['code']}"
            )
            locations = session.get(state_url, headers=_headers).json()[
                "vendor-search-results"
            ]
            for _ in locations:
                hours = []
                for hr in _["weeklySchedule"]["calendars"]:
                    if hr["scheduleDescription"] == "Business":
                        for hh in hr["schedule"]:
                            hours.append(f"{hh['weekDay']}: {hh['description']}")
                page_url = (
                    f"https://order.pizzapatron.com/menu/{_['slug']}?showInfoModal=true"
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["streetAddress"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["address"]["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["address"]["country"],
                    phone=_["phoneNumber"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
