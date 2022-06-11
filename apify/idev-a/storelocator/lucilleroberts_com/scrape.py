from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lucilleroberts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://lucilleroberts.com/"
    base_url = "https://lucilleroberts.com/clubs"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var clubs =")[1]
            .split("var mDefaults")[0]
            .strip()[:-1]
        )
        for _ in locations:
            page_url = base_url + "/" + _["slug"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for tr in sp1.select("table.table-condensed tr"):
                hours.append(" ".join(tr.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["code"],
                street_address=_["address1"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
