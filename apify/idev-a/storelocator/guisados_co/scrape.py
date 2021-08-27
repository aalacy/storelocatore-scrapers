from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("guisados")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.guisados.la"
    base_url = "https://www.guisados.la/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("#content div.col div.row.sqs-row")
        logger.info(f"{len(links)} found")
        for link in links:
            hours = []
            addr = parse_address_intl(
                " ".join(link.select("h2")[-1].stripped_strings).replace(",", "")
            )
            for hh in link.select("p"):
                if "Takeout" in hh.text or "located" in hh.text:
                    continue
                if "SERVED" in hh.text:
                    break
                if not hh.text.strip():
                    continue
                hours.append(" ".join(hh.stripped_strings).split("(")[0].strip())
            _pp = link.select("h3")[-1]
            phone = ""
            if _pp and _pp.text:
                phone = list(_pp.stripped_strings)[-1]
            ss = json.loads(link.select_one("div.map-block")["data-block-json"])
            yield SgRecord(
                page_url=base_url,
                location_name=link.h2.text.strip(),
                street_address=ss["location"]["addressLine1"],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=ss["location"]["mapLat"],
                longitude=ss["location"]["mapLng"],
                hours_of_operation="; ".join(hours).replace("–", "-").replace("—", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
