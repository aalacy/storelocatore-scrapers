from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com.cn"
base_url = "https://www.amplifon.com.cn/wp-json/amplifon/v1/store?province=0&city=0&geoSearch=false"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            city = _["city"]
            if type(city) == dict:
                city = city["label"]
            yield SgRecord(
                page_url="https://www.amplifon.com.cn/store-locator",
                store_number=_["order"],
                location_name=_["title"],
                street_address=_["address"],
                city=city,
                state=_["province"]["label"],
                latitude=_["coordinate"]["lat"],
                longitude=_["coordinate"]["lng"],
                country_code="CN",
                phone=_["tel"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
