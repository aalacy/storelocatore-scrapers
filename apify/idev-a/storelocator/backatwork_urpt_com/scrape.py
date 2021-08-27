from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("backatwork.urpt.com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://backatwork.urpt.com"
    base_url = "https://backatwork.urpt.com/find-a-location/"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var locations =")[1]
            .split("var map")[0]
            .strip()[:-1]
        )
        logger.info(f"{len(locations)}")
        for _ in locations:
            if _["is_coming_soon"] == "1":
                continue
            sp1 = bs(session.get(_["href"], headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select_one("span.hours-content").stripped_strings:
                if "Please call" in hh:
                    break
                hours.append(hh)
            logger.info(_["href"])
            yield SgRecord(
                page_url=_["href"],
                store_number=_["id"],
                location_name=_["name"][0],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("–", "-")
                .replace("\xa0", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
