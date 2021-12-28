from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com"
urls = {
    "IN": "https://www.amplifon.com/web/in/store-locator",
    "HU": "https://www.amplifon.com/web/hu/hallaskozpont-kereso",
    "PL": "https://www.amplifon.com/web/pl/nasze-gabinety",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = json.loads(
                session.get(base_url, headers=_headers)
                .text.split("var shopLocator=")[1]
                .split("var amplifonShopURL=")[0]
                .strip()[:-1]
            )
            for _ in locations:
                page_url = f"{base_url}/-/store/amplifon-point/{_['shopNumber']}/{_['shopNameForUrl']}/{_['cityForUrl']}/{_['addressForUrl']}"
                if country == "country":
                    page_url = base_url
                state = _["province"]
                if state == "0":
                    state = ""
                phone = _["phoneInfo1"]
                if not phone:
                    phone = _.get("phoneNumber1")
                if not phone:
                    phone = _.get("phoneNumber2")
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["shopName"],
                    street_address=_["address"],
                    city=_["city"],
                    state=state,
                    zip_postal=_["cap"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=_["openingTime"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
