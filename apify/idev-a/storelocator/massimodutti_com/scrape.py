from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, Grain_8, SearchableCountries
from tenacity import retry, stop_after_attempt, wait_fixed
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("massimodutti")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massimodutti.com/"
base_url = "https://www.massimodutti.com/itxrest/2/bam/store/34009527/physical-store?appId=1&languageId=-1&latitude={}&longitude={}"

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


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def _d(url):
    with SgRequests(proxy_country="us", retries_with_fresh_proxy_ip=10) as http:
        res = http.get(url, headers=_headers)
        if res.status_code != 200:
            raise Exception
        return res.json()["closerStores"]


def fetch_records(search):
    for lat, lng in search:
        try:
            locations = _d(base_url.format(lat, lng))
        except:
            locations = []
        if locations:
            logger.info(f"{search.current_country(), len(locations)}")
            for store in locations:
                hours = []
                for hr in store.get("openingHours", {}).get("schedule", []):
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
                    locator_domain=locator_domain,
                )

        else:
            logger.warning(base_url.format(lat, lng))


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
