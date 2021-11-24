from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gradepowerlearning")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://gradepowerlearning.com/"
    base_url = "https://gradepowerlearning.com/locations/"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var olc_elements =")[1]
            .split("var olc_in_page_data")[0]
            .strip()[:-1]
        )["locationData"]
        for x, _ in locations.items():
            if not _["address"] and not _["city"] and not _["prov"]:
                continue
            logger.info(_["url"])
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(
                    session.get(_["url"], headers=_headers).text, "lxml"
                ).select("dl.margin-b-0.clearfix > div")
            ]
            yield SgRecord(
                page_url=_["url"],
                store_number=x,
                location_name=_["name"],
                street_address=bs(_["address"], "lxml").text.strip(),
                city=_["city"],
                state=_["prov"],
                zip_postal=_["postal"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
