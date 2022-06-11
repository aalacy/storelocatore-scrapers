from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dealz.es"
base_url = "https://dealz.es/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        data = {
            "action": "get_stores",
            "lat": "40.4167754",
            "lng": "-3.7037902",
            "radius": "1000",
            "categories[0]": "",
        }
        locations = session.post(base_url, headers=_headers, data=data).json()
        for key, _ in locations.items():
            page_url = _["gu"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(
                sp1.select_one("div.store_locator_single_address").stripped_strings
            )[1:]
            zip_postal = addr[-1].split(",")[-1].strip().split()[-1]
            city = _["ct"]
            if not city:
                city = " ".join(addr[-1].split(",")[0].strip().split()[:-1])
            if not zip_postal.isdigit():
                zip_postal = ""
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
                city=city,
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Spain",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=", ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
