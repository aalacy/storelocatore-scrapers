from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("familyfreshmarket")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.familyfreshmarket.com/"
    base_url = "https://www.familyfreshmarket.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(_.select_one(".address").stripped_strings)
            hours = []
            for hh in sp1.select("table.hours tr")[1:]:
                hours.append(
                    f"{hh.select('td')[0].text.strip()}: {hh.select('td')[1].text.strip()}"
                )
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("/")[-1],
                location_name=_.h3.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.select_one(".phone").text.strip(),
                locator_domain=locator_domain,
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
