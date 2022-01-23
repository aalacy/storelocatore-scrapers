from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("gaes")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amplifon.com"
ss_urls = {
    "IN": "https://www.amplifon.com/web/in/store-locator",
}

hu_url = "https://www.amplifon.com/hu/sitemap.xml"
pl_url = "https://www.amplifon.com/pl/sitemap.xml"


def fetch_data():
    with SgRequests() as session:
        for country, base_url in ss_urls.items():
            locations = json.loads(
                session.get(base_url, headers=_headers)
                .text.split("var shopLocator=")[1]
                .split("var amplifonShopURL=")[0]
                .strip()[:-1]
            )
            for _ in locations:
                page_url = f"{base_url}/-/store/amplifon-point/{_['shopNumber']}/{_['shopNameForUrl'].lower()}/{_['cityForUrl'].lower()}/{_['addressForUrl'].lower()}"
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


def fetch_others():
    with SgRequests() as session:
        urls = {}
        urls["hu"] = bs(session.get(hu_url, headers=_headers).text, "lxml").select(
            "loc"
        )
        urls["pl"] = bs(session.get(pl_url, headers=_headers).text, "lxml").select(
            "loc"
        )
        for country, url1 in urls.items():
            for url in url1:
                page_url = url.text
                if (
                    "pl/nasze-gabinety/" not in page_url
                    and "hu/hallaskozpont-kereso/" not in page_url
                ):
                    continue

                if len(page_url.split("/")) < 7:
                    continue

                if "store-detail" in page_url:
                    continue

                logger.info(f"[***] {page_url}")
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                _ = json.loads(sp1.find("script", type="application/ld+json").string)
                phone = ""
                if sp1.select_one("span.phone-list"):
                    try:
                        phone = list(
                            sp1.select_one("span.phone-list").stripped_strings
                        )[0]
                    except:
                        pass
                hours = []
                for hh in _["openingHoursSpecification"]:
                    day = hh["dayOfWeek"]
                    hours.append(f"{day}: {hh['opens']} - {hh['closes']}")
                addr = _["address"]
                state = addr.get("addressRegion")
                if (
                    state.replace("(", "")
                    .replace(")", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    state = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=addr["streetAddress"],
                    city=addr["addressLocality"],
                    state=state,
                    zip_postal=addr.get("postalCode"),
                    latitude=_["geo"]["latitude"],
                    longitude=_["geo"]["longitude"],
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

        results = fetch_others()
        for rec in results:
            writer.write_row(rec)
