from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.wynnstay.co.uk",
    "referer": "https://www.wynnstay.co.uk/wynnstaystores",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wynnstay.co.uk"
base_url = "https://www.wynnstay.co.uk/amlocator/index/ajax/"


def fetch_records(http, search):
    for lat, lng in search:
        data = {
            "lat": str(lat),
            "lng": str(lng),
            "radius": "100",
            "product": "0",
            "category": "0",
            "attributes[0][name]": "1",
            "attributes[0][value]": "",
            "attributes[1][name]": "2",
            "attributes[1][value]": "",
            "attributes[2][name]": "3",
            "attributes[2][value]": "",
            "attributes[3][name]": "4",
            "attributes[3][value]": "",
            "attributes[4][name]": "5",
            "attributes[4][value]": "",
            "attributes[5][name]": "6",
            "attributes[5][value]": "",
            "attributes[6][name]": "7",
            "attributes[6][value]": "",
            "attributes[7][name]": "8",
            "attributes[7][value]": "",
            "attributes[8][name]": "9",
            "attributes[8][value]": "",
            "sortByDistance": "1",
        }
        locations = http.post(base_url, headers=_headers, data=data).json()["items"]
        logger.info(f"[{lat, lng}] {len(locations)}")
        for _ in locations:
            search.found_location_at(_["lat"], _["lng"])
            page_url = f"https://www.wynnstay.co.uk/wynnstaystores/{_['url_key']}"
            hours = []
            if _["schedule_string"]:
                for day, hh in json.loads(_["schedule_string"]).items():
                    start = f"{hh['from']['hours']}:{hh['from']['minutes']}"
                    end = f"{hh['to']['hours']}:{hh['to']['minutes']}"
                    hours.append(f"{day}: {start} - {end}")
            street_address = _["address"]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = _["city"]
            if city:
                city = city.split(",")[-1].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=city,
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=50
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
