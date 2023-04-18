from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aldi")
locator_domain = "https://www.aldi.ie"
base_url = (
    "https://www.aldi.ie/api/store-finder/search?latitude={}&longitude={}&page={}"
)
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "Host": "www.aldi.ie",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def fetch_records(http, search):
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        page = 0
        while True:
            data = http.get(base_url.format(lat, lng, page), headers=headers).json()
            locations = data["results"]
            logger.info(f"[{lat}, {lng}] [page {page}] [{progress}] [{len(locations)}]")
            for _ in locations:
                hours = []
                for hh in _["openingTimes"]:
                    times = (
                        hh.get("hours", "")
                        .replace("nbsp;", " ")
                        .replace("&ndash;", "-")
                    )
                    if hh["closed"]:
                        times = "closed"
                    hours.append(f"{hh['day']}: {times}")
                page_url = f"https://www.aldi.ie/store/{_['code']}"
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["name"].split("-")[-1].strip(),
                    city=_["address"][0].split(",")[0].strip(),
                    state=_["address"][0].split(",")[-1].strip(),
                    zip_postal=_["address"][-1],
                    latitude=_["latlng"]["lat"],
                    longitude=_["latlng"]["lng"],
                    country_code="Ireland",
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

            page = data["pagination"].get("next")
            if not page:
                break


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.IRELAND], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=3
        )
    ) as writer:
        with SgRequests(proxy_country="us") as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
