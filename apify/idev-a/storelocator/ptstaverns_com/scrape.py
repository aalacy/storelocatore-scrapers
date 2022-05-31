from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

logger = SgLogSetup().get_logger("ptstaverns")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def _coord(locs, nn):
    for loc in locs:
        if loc.split(";marker")[1].split("=")[0] == nn:
            return json.loads(loc.split(";contentString")[0])


def fetch_data():
    locator_domain = "https://www.ptstaverns.com"
    base_url = "https://www.ptstaverns.com/locations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = res.split("latLng=")[1:]
        locations = bs(res, "lxml").select("table#location-list tbody tr")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("div.loc-address p").stripped_strings)
            phone = ""
            if _p(addr[-1]):
                phone = addr[-1]
                del addr[-1]
            hours_of_operation = sp1.select("div.loc-address p")[-1].text.strip()
            nn = _.img["data-id"].replace("marker", "")
            latlng = _coord(locs, nn)
            location_type = _.img["alt"].split("for")[-1].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                latitude=latlng["lat"],
                longitude=latlng["lng"],
                location_type=location_type,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
