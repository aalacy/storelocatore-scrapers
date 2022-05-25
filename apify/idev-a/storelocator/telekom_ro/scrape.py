from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog
import tenacity

session = SgRequests(proxy_country="gb")

logger = sglog.SgLogSetup().get_logger("telekom_ro")

_headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "fix.telekom.ro",
    "Referer": "https://fix.telekom.ro/magazine/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fix.telekom.ro"
base_url = "https://fix.telekom.ro/blocks/business/magazine/magazineLocatorJson.jsp"
json_url = "https://fix.telekom.ro/blocks/business/magazine/magazineLocatorJson.jsp?storeCity={}&storeTypes=cosmote&storeTypes=orange"


@tenacity.retry(wait=tenacity.wait_fixed(10))
def get_json(city):

    with SgRequests(proxy_country="ro") as session:
        response = session.get(json_url.format(city["cityEncoded"]), headers=_headers)
        logger.info(
            f"crawling {city['cityEncoded']} , Stores Found: {city['storeCount']} >> Response: {response.status_code}"
        )
        locations = response.json()
        return locations


def fetch_data():
    cities = session.get(base_url, headers=_headers).json()
    logger.info(f"Total Cities: {len(cities)}")
    for city in cities:
        try:
            locations = get_json(city)
        except:
            break
        for _ in locations:
            street_address = _["address"].replace(_["city"], "").strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            location_type = ""
            if "orange" in _["type"]:
                location_type = "Orange Store"
            elif "cosmote" in _["type"]:
                location_type = "TKR Magazine"
            yield SgRecord(
                page_url="https://fix.telekom.ro/magazine/",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["county"],
                zip_postal=_["postalCode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Romania",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=_["schedule"],
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
