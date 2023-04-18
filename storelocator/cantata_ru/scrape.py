from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from urllib.parse import urlencode
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://cantata.ru"
base_url = "https://cantata.ru/galleries"
json_url = "https://cantata.ru/cantata/shops?{}"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        token = res.headers.get("set-cookie").split("token=")[1].split(";expires")[0]
        countries = json.loads(
            bs(res.text, "lxml").select_one("script#__NEXT_DATA__").text
        )["props"]["pageProps"]["initialState"]["locations"]["items"]
        for country in countries:
            regions = country["items"]
            for region in regions:
                cities = region["items"]
                for city in cities:
                    param = {
                        "city": city["name"],
                        "token": token,
                    }
                    logger.info(city["name"])
                    locations = session.get(
                        json_url.format(urlencode(param)), headers=_headers
                    ).json()["data"]
                    for _ in locations:
                        hours = []
                        for hh in _.get("working_times", []):
                            hours.append(
                                f"{days[hh['dayFrom']]} - {days[hh['dayTo']]}: {hh['timeFrom']} - {hh['timeTo']}"
                            )

                        yield SgRecord(
                            page_url=base_url,
                            store_number=_["id"],
                            location_name=_["name"],
                            city=city["name"],
                            state=region["name"],
                            latitude=_["lat"],
                            longitude=_["lon"],
                            country_code=country["name"],
                            location_type=_["type"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(hours),
                        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
