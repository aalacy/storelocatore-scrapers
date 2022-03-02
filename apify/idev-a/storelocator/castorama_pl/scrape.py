from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.castorama.pl"
base_url = "https://www.castorama.pl/informacje/sklepy"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.block-shops-content div.row")
        for _ in locations:
            page_url = _.select("a")[-1]["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            info = sp1.select_one("div#subdomain-market-map")
            hours = []
            for key, val in info.attrs.items():
                if "data-market-hours" not in key:
                    continue
                day = key.replace("data-market-hours-", "")
                hours.append(f"{day}: {val}")

            yield SgRecord(
                page_url=page_url,
                store_number=info["data-market-id"],
                location_name=info["data-market-name"],
                street_address=info["data-market-street"],
                city=info["data-market-city"],
                state=info["data-market-region"],
                zip_postal=info["data-market-code"],
                country_code="PL",
                phone=info["data-market-phone"],
                latitude=info["data-market-latitude"],
                longitude=info["data-market-longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
