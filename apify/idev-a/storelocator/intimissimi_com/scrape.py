from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("intimissimi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.intimissimi.com/"
base_url = "https://www.intimissimi.com/on/demandware.store/Sites-intimissimi-ww-Site/en_WS/Stores-FindStores?radius=100&lat={}&long={}&geoloc=false"


def _v(val):
    return (
        val.replace("Castell-Platja D&apos;aro-Platja D&apos;aro", "")
        .replace("Cornate D&apos;adda", "")
        .replace("AFFI CCLE GRAND&apos;AFFI", "")
        .replace(
            "&quot;Via Rodolfo Rodolfo Morandi 16  - CCle &quot;&quot;Ariosto&quot;&quot;&quot;",
            "",
        )
        .replace("&apos;", "'")
        .strip()
    )


def fetch_records(http, search):
    for lat, lng in search:
        res = http.get(base_url.format(lat, lng), headers=_headers)
        if res.status_code == 200:
            locations = res.json()["stores"]
            logger.info(f"[{search.current_country()}] found: {len(locations)}")
            for store in locations:
                hours = []
                for hr in store.get("storeHours", []):
                    times = hr["phases"]
                    if not hr["phases"]:
                        times = "Closed"
                    hours.append(f"{hr['name']}: {times}")

                street_address = store["address1"]
                if store.get("address2"):
                    street_address += " " + store["address2"]
                page_url = f'https://www.intimissimi.com/world/stores/{store["name"].lower().replace(" ","_")}/{store["ID"]}.html'
                if store["ID"] == "IBO4":
                    page_url = ""
                city = store.get("city", "")
                if city:
                    street_address = street_address.replace(city, "")
                zip_postal = store.get("postalCode", "")
                if zip_postal:
                    street_address = street_address.replace(zip_postal, "")
                yield SgRecord(
                    page_url=page_url,
                    store_number=store["ID"],
                    location_name=_v(store["name"]),
                    street_address=_v(street_address).replace(",", ""),
                    city=_v(city),
                    state=store.get("state", ""),
                    zip_postal=zip_postal,
                    latitude=store["latitude"],
                    longitude=store["longitude"],
                    phone=store.get("phone"),
                    country_code=store["countryCode"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=500
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=15
        )
    ) as writer:
        with SgRequests(proxy_country="us") as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
