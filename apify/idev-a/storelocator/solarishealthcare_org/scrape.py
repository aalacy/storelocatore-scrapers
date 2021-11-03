from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("solarishealthcare")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://solarishealthcare.org"
base_url = "http://solarishealthcare.org/locations/#list"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("article div.entry-content p")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.text.strip():
                continue
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(link.stripped_strings)
            ss = json.loads(sp1.select_one("div.wpgmza_map")["data-settings"])

            yield SgRecord(
                page_url=page_url,
                location_name=" ".join(link.strong.stripped_strings),
                street_address=addr[2],
                city=addr[3].split(",")[0].strip(),
                state=addr[3].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[3].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2].split(":")[-1].replace("Phone", "").strip(),
                locator_domain=locator_domain,
                latitude=ss["map_start_lat"],
                longitude=ss["map_start_lng"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
