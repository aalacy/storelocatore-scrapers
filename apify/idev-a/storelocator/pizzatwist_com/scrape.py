from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizzatwist")

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Host": "pizzatwist.com",
    "Origin": "https://pizzatwist.com",
    "Referer": "https://pizzatwist.com/location",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pizzatwist.com/"
base_url = "https://pizzatwist.com/pizzatwist/Front_controller/get_order_data"
city_url = "https://pizzatwist.com/pizzatwist/Front_controller/get_city_code"
store_url = "https://pizzatwist.com/pizzatwist/Front_controller/search_store"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        states = session.get(base_url).json()["states"]
        for state in states:
            payload = {"state_id": state["id"]}
            cities = session.post(city_url, headers=_headers, json=payload).json()[
                "city"
            ]
            if not cities:
                continue
            logger.info(f"[{state['name']}] {len(cities)} cities")
            for city in cities:
                data = {"state_id": state["id"], "store_city": city["id"]}
                locations = session.post(store_url, headers=_headers, json=data).json()[
                    "store_details"
                ]
                logger.info(
                    f"[{state['name']}] [{city['name']}] {len(locations)} locations"
                )
                for _ in locations:
                    hours = []
                    for hh in _["store_week_day_time"]:
                        if not hh["day_name"]:
                            continue
                        hours.append(f"{hh['day_name']}: {hh['open_time']}")

                    yield SgRecord(
                        page_url="https://pizzatwist.com/location",
                        store_number=_["ai_store_id"],
                        location_name=_["store_name"],
                        street_address=_["store_address"],
                        city=_["city_name"],
                        state=_["state_name"],
                        zip_postal=_["pincode"],
                        country_code="US",
                        phone=_["store_phone"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
