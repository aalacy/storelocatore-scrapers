from typing import Iterable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("massimodutti")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massimodutti.com/"
base_url = "https://www.massimodutti.com/itxrest/2/bam/store/34009456/physical-store?appId=1&languageId=-1&latitude={}&longitude={}&favouriteStores=false&lastStores=false&closerStores=true&min=10&radioMax=100&receiveEcommerce=false&showBlockedMaxPackage=false"

days = [
    "",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    for lat, lng in search:
        http.clear_cookies()
        res = http.get(base_url.format(lat, lng), headers=_headers)
        if res.status_code != 200:
            continue
        locations = res.json()["closerStores"]
        logger.info(f"{len(locations)}")
        for store in locations:
            hours = []
            for hr in store.get("openingHours", {}).get("schedule", []):
                import pdb

                pdb.set_trace()
                times = f"{hr['timeStripList'][0]['initHour']} - {hr['timeStripList'][0]['endHour']}"
                if len(hr["weekdays"]) == 1:
                    hh = hr["weekdays"][0]
                    hours.append(f"{days[hh]}: {times}")
                else:
                    day = f'{days[hr["weekdays"][0]]} to {days[hr["weekdays"][-1]]}'
                    hours.append(f"{day}: {times}")
            phone = ""
            if store.get("phones"):
                phone = store["phones"][0]

            _streat = (
                "-".join(store["name"].split())
                .lower()
                .replace(".", "")
                .replace(",", "")
            )
            if store["state"]:
                _state = "-".join(store["state"].split()).lower()
            else:
                _state = "-".join(store["city"].split()).lower()

            page_url = f'https://www.massimodutti.com/us/store-locator/{_state}/{_streat}/{store["latitude"]},{store["longitude"]}/{store["id"]}'
            yield SgRecord(
                page_url=page_url,
                store_number=store["id"],
                location_name=store["name"],
                street_address=" ".join(store["addressLines"]),
                city=store["city"],
                state=store["state"],
                zip_postal=store["zipCode"],
                latitude=store["latitude"],
                longitude=store["longitude"],
                phone=phone,
                country_code=store["countryCode"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(country_codes=SearchableCountries.ALL)
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests(proxy_country="us") as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
