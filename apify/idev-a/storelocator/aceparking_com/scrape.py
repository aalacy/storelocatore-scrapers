from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from datetime import date, timedelta
import urllib.parse
import dirtyjson as json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("quizclothing")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aceparking.com"
base_url = "https://space.aceparking.com/site/results?"


def params(hourly, zip):
    return {
        "hourly": str(hourly),
        "address": str(zip),
        "Reservation[date_start]": date.today().strftime("%a, %m/%d"),
        "start_time": "10:07",
        "Reservation[date_end]": (date.today() + timedelta(days=1)).strftime(
            "%a, %m/%d"
        ),
        "end_time": "19:07",
    }


def _coord(locs, name):
    coord = {}
    for loc in locs:
        _ = loc.split("function")[0]
        if "icon" in loc:
            if _.split("title:")[1].split("icon")[0].strip()[1:-2].strip() == name:
                coord = json.loads(_.split("position:")[1].split("map")[0].strip()[:-1])
                break
    return coord


def fetch_data(search):
    with SgRequests() as session:
        for zip in search:
            for hourly in range(1, 3):
                url = base_url + urllib.parse.urlencode(params(hourly, zip))
                logger.info(url)
                res = session.get(url, headers=_headers)
                locs = res.text.split("new google.maps.Marker(")[2:]
                soup = bs(res, "lxml")
                if soup.select_one("div.siteResults h4.error"):
                    continue
                locations = soup.select("div.lotSection")
                try:
                    soup.select_one("div.resultAddress").text.strip().split(",")
                except:
                    continue
                if hourly == 1:
                    location_type = "daily"
                else:
                    location_type = "monthly"
                logger.info(f"[{zip}] {len(locations)}")
                for _ in locations:
                    street_address = [
                        aa.text.strip() for aa in _.select("div.infoAddress")
                    ]
                    hours = []
                    for hh in _.select("div#tabs-1 table tr"):
                        td = list(hh.stripped_strings)
                        hours.append(f"{td[0]}: {td[1]} - {td[2]}")
                    location_name = _.select_one("div.infoName").text.strip()
                    coord = _coord(locs, location_name)
                    yield SgRecord(
                        page_url="https://space.aceparking.com/site/results",
                        store_number=_["id"].split("-")[-1],
                        location_name=location_name,
                        street_address=" ".join(street_address),
                        country_code="US",
                        latitude=coord.get("lat"),
                        longitude=coord.get("lng"),
                        locator_domain=locator_domain,
                        location_type=location_type,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], granularity=Grain_8()
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
