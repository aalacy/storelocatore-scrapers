from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.dogtopia.com"
base_url = "https://www.dogtopia.com/wp-json/store-locator/v1/locations.json"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(base_url, headers=_headers).json()
        for store in store_list:
            addr = store["store_info"]["location_address_info"][0]
            hours = []
            if store["store_info"]["location_hours_info"]:
                _hr = store["store_info"]["location_hours_info"][0]
                if _hr.get("coming_soon_checkbox") == "on":
                    continue
                for day in days:
                    day = day.lower()
                    open = f"{day}_open"
                    close = f"{day}_close"
                    if _hr.get(open):
                        times = f"{_hr[open]}-{_hr[close]}"
                    else:
                        times = "closed"
                    hours.append(f"{day}: {times}")
            if not hours:
                sp1 = bs(
                    session.get(
                        store["link"].replace("locations/", ""), headers=_headers
                    ).text,
                    "lxml",
                )
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.uk-table tr")
                ]

            yield SgRecord(
                page_url=store["link"].replace("locations/", ""),
                store_number=addr["location_id"],
                location_name=store["title"]["raw"],
                street_address=addr["location_street_address"]
                .replace(",", " ")
                .strip(),
                city=addr["location_city"],
                state=addr["location_state_prov"],
                latitude=addr["location_coordinates"]["latitude"],
                longitude=addr["location_coordinates"]["longitude"],
                zip_postal=addr["location_zip_postal"],
                country_code=addr["location_country"],
                locator_domain=locator_domain,
                phone=addr["location_phone"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
