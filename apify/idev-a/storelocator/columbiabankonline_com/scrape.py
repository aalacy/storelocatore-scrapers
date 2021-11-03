from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("columbiabankonline")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.columbiabankonline.com"
base_url = "https://www.columbiabankonline.com/branch-locations"


def fetch_data():
    with SgRequests() as session:
        links = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("input#map_value")["value"]
            .replace("&quot;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#39;", "'")
        )
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + bs(link[0], "lxml").a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = parse_address_intl(ss["address"]["addressLocality"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            if ss.get("openingHours"):
                hours = ss["openingHours"]
            elif ss.get("department") and ss["department"][0].get("openingHours"):
                hours = ss["department"][0]["openingHours"]
            try:
                yield SgRecord(
                    page_url=page_url,
                    location_name=ss["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=ss["telephone"],
                    locator_domain=locator_domain,
                    latitude=link[1],
                    longitude=link[2],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
