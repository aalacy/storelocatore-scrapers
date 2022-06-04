from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://celebritytanning.com",
    "referer": "https://celebritytanning.com/find-a-salon/?location=37RP+3R%20Dearing,%20KS,%20USA&radius=100",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
}

locator_domain = "https://celebritytanning.com"
base_url = "https://celebritytanning.com/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        data = "action=get_all_stores&lat=&lng="
        locations = session.post(base_url, headers=_headers, data=data).json()
        for x, _ in locations.items():
            logger.info(_["gu"])
            sp1 = bs(session.post(_["gu"], headers=header1).text, "lxml")
            addr = list(
                sp1.select_one("div.store_locator_single_address").stripped_strings
            )[1:]
            hours = list(
                sp1.select_one(
                    "div.store_locator_single_opening_hours"
                ).stripped_strings
            )[1:]
            yield SgRecord(
                page_url=_["gu"],
                store_number=_["ID"],
                location_name=_["na"],
                street_address=_["st"],
                city=_["ct"],
                state=addr[-1].split(",")[-2].strip(),
                zip_postal=_["zp"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["te"],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
                hours_of_operation="; ".join(hours).replace("o'Clock", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
