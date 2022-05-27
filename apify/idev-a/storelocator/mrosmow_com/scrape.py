from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("")
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.replace("&#8211;", "-")
        .replace("&#038;", "")
        .replace("–", "-")
        .replace("&#8217;", "'")
        .strip()
    )


def fetch_data():
    locator_domain = "https://mrosmow.com"
    base_url = "https://mrosmow.com/wp-admin/admin-ajax.php?action=store_search&lat=43.653226&lng=-79.3831843&max_results=750&search_radius=500&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += _["address2"]
            hours = []
            for hh in bs(_["hours"], "lxml").select("tr"):
                hours.append(f"{hh.select('td')[0].text}: {hh.select('td')[1].text}")
            state = _["state"]
            zip_postal = _["zip"]
            if not state or not zip_postal:
                logger.info(_["url"])
                info = json.loads(
                    session.get(_["url"], headers=_headers)
                    .text.split(".fusion_maps(")[1]
                    .split("google.maps")[0]
                    .strip()[:-1]
                    .strip()[:-2]
                )
                addr = list(
                    bs(info["addresses"][0]["address"], "lxml").stripped_strings
                )
                state = addr[-1].split()[-3].strip().replace(",", "")
                zip_postal = " ".join(addr[-1].split()[2:])

            yield SgRecord(
                page_url=_["url"],
                store_number=_["id"],
                location_name=_valid(_["store"]),
                street_address=street_address,
                city=_["city"],
                state=state,
                latitude=_["lat"],
                longitude=_["lng"],
                phone=_["phone"],
                zip_postal=zip_postal,
                country_code=_["country"],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
