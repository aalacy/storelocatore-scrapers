from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fitness19.com"
base_url = "https://www.fitness19.com/?search_type=location&s="


def _coord(locs, name):
    for loc in locs:
        _ = json.loads(
            loc.split(");")[0]
            .replace("new google.maps.LatLng(", '"')
            .replace("),", '",')
            .replace("map,", '"map",')
            .replace("\n", "")
            .replace("\t", "")
        )
        if name in _["title"]:
            return _

    return {}


def fetch_data():
    with SgRequests() as session:
        res0 = session.get(base_url, headers=_headers).text
        locs = res0.split("new google.maps.Marker(")[1:]
        soup = bs(res0, "lxml")
        locations = soup.select("section#locations_list div.row")
        for _ in locations:
            page_url = _.a["href"]
            addr = list(_.select_one("p.location_address").stripped_strings)
            phone = ""
            if _.select_one("p.location_phone"):
                phone = _.select_one("p.location_phone").text.strip()
            location_name = _.h2.text.strip()
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            hours_of_operation = ""
            hours = []
            if sp1.select_one("section#location-hours"):
                if sp1.select_one("section#location-hours dl"):
                    hours = list(
                        sp1.select_one("section#location-hours dl").stripped_strings
                    )
                    hours_of_operation = ": ".join(hours)
            elif sp1.select_one("div.gym-hours"):
                for hh in sp1.select("div.gym-hours p"):
                    if "open" in hh.text.lower():
                        continue
                    hours.append(hh.text.strip())
                hours_of_operation = "; ".join(hours)
            city = addr[-1].split(",")[0].strip()
            state = addr[-1].split(",")[1].strip().split()[0].strip()
            coord = _coord(locs, f"{city}, {state}").get("position", ",").split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=" ".join(addr[:-1]).split("(")[0],
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
