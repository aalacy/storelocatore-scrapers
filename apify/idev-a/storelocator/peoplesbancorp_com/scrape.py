from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
import dirtyjson

logger = SgLogSetup().get_logger("peoplesbancorp")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.peoplesbancorp.com"
base_url = "https://locations.peoplesbancorp.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        regions = soup.select("ul.region-map-list a")
        for region in regions:
            locations = json.loads(
                session.get(region["href"], headers=_headers)
                .text.split('"markerData":')[1]
                .split("};</script>")[0]
            )
            for loc in locations:
                url = json.loads(bs(loc["info"], "lxml").text)["url"]
                logger.info(url)
                res = session.get(url, headers=_headers).text
                _info = json.loads(
                    res.split("$config.defaultListData =")[1]
                    .split("$config.regionData")[0]
                    .strip()[1:-2]
                    .replace('\\\\\\"', "'")
                    .replace('\\"', '"')
                    .replace("\\/", "/")
                )
                for _ in _info:
                    page_url = _["url"]
                    if (
                        page_url
                        == "https://locations.peoplesbancorp.com/oh/pomeroy/31637-dead-mans-curve-rd.html"
                    ):
                        continue
                    street_address = _["address_1"]
                    if _["address_2"]:
                        street_address += " " + _["address_2"]
                    hours = []
                    if _.get("hours_sets:primary"):
                        _hr = json.loads(_["hours_sets:primary"])
                        if _hr.get("days"):
                            for day, hh in _hr["days"].items():
                                times = hh
                                if (
                                    type(hh)
                                    == dirtyjson.attributed_containers.AttributedList
                                ):
                                    temp = []
                                    for hr in hh:
                                        temp.append(f"{hr['open']}-{hr['close']}")
                                    times = ", ".join(temp)
                                hours.append(f"{day}: {times}")
                        else:
                            hours = ["closed"]
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["lid"],
                        location_name=_["location_name"],
                        street_address=street_address,
                        city=_["city"],
                        state=_["region"],
                        zip_postal=_["post_code"],
                        country_code="CA",
                        phone=_["local_phone"],
                        latitude=_["lat"],
                        longitude=_["lng"],
                        location_type=_["Location Type_CS"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
