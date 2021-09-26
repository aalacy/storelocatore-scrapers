from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("potbelly")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.potbelly.com"
base_url = "https://www.potbelly.com/location-directory"


def _t(val):
    return val.split()[-1]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        columns = json.loads(soup.find("script", type="application/json").string)[
            "props"
        ]["pageProps"]["columns"]
        logger.info(f"{len(columns)} found")
        for key, column in columns.items():
            for state in column:
                for link in state["locations"]:
                    page_url = locator_domain + "/locations/" + link["url"]
                    logger.info(page_url)
                    url = f"https://api.prod.potbelly.com/v1/restaurants/byslug/{link['url'].split('/')[-1]}?includeHours=true"
                    res = session.get(url, headers=_headers)
                    if res.status_code != 200:
                        continue
                    _ = res.json()
                    hours = []
                    if _["calendars"]:
                        count = 0
                        for hh in _["calendars"][0]["ranges"]:
                            if count > 6:
                                break
                            count += 1
                            hours.append(
                                f"{hh['weekday']}: {_t(hh['start'])} - {_t(hh['end'])}"
                            )
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["name"],
                        store_number=_["id"],
                        street_address=_["streetaddress"],
                        city=_["city"],
                        state=_["state"],
                        zip_postal=_["zip"],
                        country_code=_["country"],
                        phone=_["telephone"],
                        latitude=_["latitude"],
                        longitude=_["longitude"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
