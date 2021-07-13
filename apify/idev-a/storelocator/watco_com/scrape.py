from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import re

logger = SgLogSetup().get_logger("watco")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.watco.com"
base_url = "https://www.watco.com/Leaflet_Map_11-05-2020/data/Labels_5.js"

urls = []


def fetch_data():
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var json_Labels_5 =")[1]
            .strip()
        )["features"]
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["properties"]["descriptio"]
            if page_url in urls:
                continue
            urls.append(page_url)
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            if sp1.find("h4", string=re.compile(r"^Operations")):
                addr = list(
                    sp1.find("h4", string=re.compile(r"^Operations"))
                    .find_parent()
                    .stripped_strings
                )[1:]
                street_address = addr[0]
                city = addr[1].split(",")[0].strip()
                state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
                phone = addr[-1]
            else:
                continue
            yield SgRecord(
                page_url=page_url,
                location_name=link["properties"]["Name"],
                street_address=street_address.replace("–", "-"),
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["geometry"]["coordinates"][1],
                longitude=link["geometry"]["coordinates"][0],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
