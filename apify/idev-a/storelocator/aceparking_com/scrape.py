from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from urllib.parse import urlencode
import dirtyjson as json
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aceparking")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aceparking.com"
base_url = "https://space.aceparking.com/site/results?"


def params(hourly, row):
    return {
        "hourly": str(hourly),
        "address": f"{', '.join(row)}, USA",
    }


def get_city_list():
    city_list = []
    logger.info("... reading city list csv")
    with open("./uscities.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = [row["city"], row["state_id"]]
            if val not in city_list:
                city_list.append(val)

        logger.info(f"filtered {len(city_list)} cities from csv")
        return city_list


def _coord(locs, name):
    coord = {}
    for loc in locs:
        _ = loc.split("function")[0]
        if "icon" in loc:
            if _.split("title:")[1].split("icon")[0].strip()[1:-2].strip() == name:
                coord = json.loads(_.split("position:")[1].split("map")[0].strip()[:-1])
                break
    return coord


def fetch_data(city_list):
    with SgRequests() as session:
        for row in city_list:
            for hourly in range(1, 3):
                url = base_url + urlencode(params(hourly, row))
                logger.info(url)
                res = session.get(url, headers=_headers)
                locs = res.text.split("new google.maps.Marker(")[2:]
                soup = bs(res, "lxml")
                if soup.select_one("div.siteResults h4.error"):
                    logger.warning("div.siteResults h4.error")
                    continue

                locations = soup.select("div.lotSection")
                try:
                    soup.select_one("div.resultAddress").text.strip().split(",")
                except:
                    logger.warning("div.resultAddress")
                    continue

                if hourly == 1:
                    location_type = "daily"
                else:
                    location_type = "monthly"
                logger.info(f"[{row[0]}] {len(locations)}")
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
                        street_address=" ".join(street_address).split("Lot")[0].strip(),
                        city=row[0],
                        state=row[1],
                        country_code="US",
                        latitude=coord.get("lat"),
                        longitude=coord.get("lng"),
                        locator_domain=locator_domain,
                        location_type=location_type,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        city_list = get_city_list()
        results = fetch_data(city_list)
        for rec in results:
            writer.write_row(rec)
