from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from urllib.parse import quote

logger = SgLogSetup().get_logger("littlecaesars")


def headers(city):
    return {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "es-mx",
        "content-type": "application/json",
        "origin": "https://mexico.littlecaesars.com",
        "referer": f"https://mexico.littlecaesars.com/es-mx/order/pickup/stores/search/{quote(city)}/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


locator_domain = "https://mexico.littlecaesars.com"
base_url = "https://api.cloud.littlecaesars.com/bff/api/GetClosestStores"
city_url = "https://www.britannica.com/topic/list-of-cities-and-towns-in-Mexico-2039050"


def fetch_data(session):
    cities = bs(session.get(city_url).text, "lxml").select(
        "div.topic-content ul.topic-list li a"
    )
    logger.info(f"{len(cities)} cities")
    for city in cities:
        _city = city.text.split("(")[0].strip()
        payload = {"address": {"street": "", "city": _city, "state": "", "zip": ""}}
        try:
            locations = session.post(
                base_url, headers=headers(_city), json=payload
            ).json()["stores"]
            logger.info(f"[{_city}] {len(locations)}")
        except:
            logger.info(f"[{_city}] 0")
            continue
        for _ in locations:
            hours = f"{_['storeOpenTime']} - {_['storeCloseTime']}"
            location_type = ""
            if not _["isOpen"]:
                location_type = "closed"
            addr = _["address"]
            page_url = (
                f"https://mexico.littlecaesars.com/es-mx/store/{_['locationNumber']}/"
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["locationNumber"],
                location_name=_["storeName"],
                street_address=addr["street"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Mexico",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as session:
            results = fetch_data(session)
            for rec in results:
                writer.write_row(rec)
