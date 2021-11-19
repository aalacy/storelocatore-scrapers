from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizza")

_headers = {
    "Accept": "application/json, text/plain, */*",
    "apikey": "g2ryadu2xa57eti9fu94dyend21rldwjmrv8zfhy0mt6wr9z5tbzpxx1uazlobiuc6nodmhwq8vvpixqkzu87r1eung14850hb6dz3gqmgbgghwg6024sowaum96im80",
    "Referer": "https://www.pizzahut.com.pk/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pizzahut.com.pk"
base_url = "https://web-api.pizzahut.com.pk/api/v1/trade_city"
city_url = "https://web-api.pizzahut.com.pk/api/v1/area_by_city/{}"


def fetch_data():
    with SgRequests() as session:
        cities = session.get(base_url, headers=_headers).json()["data"]
        codes = []
        for city in cities:
            locations = session.get(
                city_url.format(city["id"]), headers=_headers
            ).json()["data"]
            logger.info(f"[{city['name']}] {len(locations)} found")
            for _ in locations:
                if _["OutletCode"] in codes:
                    continue
                codes.append(_["OutletCode"])
                yield SgRecord(
                    page_url="",
                    store_number=_["ID"],
                    location_name=_["OutletName"],
                    street_address=_["AreaName"]
                    .split(city["name"])[0]
                    .replace(",", "")
                    .replace("NO 24HOURS DELIVERY", ""),
                    city=city["name"],
                    country_code="Pakistan",
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
