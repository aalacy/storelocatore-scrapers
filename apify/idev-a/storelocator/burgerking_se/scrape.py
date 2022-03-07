from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.burgerking.se"
base_url = "https://bk-se-ordering-api.azurewebsites.net/cms/sv-SE/restaurants"
payload = {
    "coordinates": {"latitude": 59.330311012767446, "longitude": 18.068330468145753},
    "radius": 400000,
}


def fetch_data():
    with SgRequests() as session:
        locations = session.put(base_url, headers=_headers, json=payload).json()["data"]
        for _ in locations:
            page_url = f"https://www.burgerking.se/restaurants/{_['slug']}"
            hours = []
            city = state = zip_postal = ""
            url = f"https://bk-se-ordering-api.azurewebsites.net/cms/sv-SE/restaurants/{_['slug']}"
            res = session.get(url, headers=_headers)
            if res.status_code == 200:
                data = res.json()["data"]
                city = data["storeLocation"]["address"]["city"]
                state = data["storeLocation"]["address"]["state"]
                zip_postal = data["storeLocation"]["address"]["postalCode"]
                for hh in data.get("storeOpeningHours", []):
                    times = "closed"
                    if hh["isOpen"]:
                        times = f"{hh['hoursOfBusiness']['opensAt'].split('T')[-1]}-{hh['hoursOfBusiness']['closesAt'].split('T')[-1]}"
                    hours.append(f"{hh['dayOfTheWeek']}: {times}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["storeName"],
                street_address=_["storeAddress"],
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["coordinates"]["latitude"],
                longitude=_["coordinates"]["longitude"],
                country_code="Sweden",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
