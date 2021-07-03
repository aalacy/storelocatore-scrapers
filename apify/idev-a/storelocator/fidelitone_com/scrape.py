from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("fidelitone")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fidelitone.com"
base_url = "https://www.fidelitone.com/locations"


def fetch_data():
    with SgRequests() as session:
        res = (
            session.get(base_url, headers=_headers)
            .text.split("var locations =")[1]
            .split("var showAll")[0]
            .strip()[:-1]
            .replace("\n", "")
            .replace("\t", "")
            .replace("\\", "")
            .replace("new google", '"new google')
            .replace("),", ')",')
        )
        links = json.loads(res)
        logger.info(f"{len(links)} found")
        for link in links:
            _ = bs(link["title"], "lxml")
            page_url = locator_domain + _.a["href"].replace(" ", "-")
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.address.stripped_strings)
            coord = link["position"].split(".LatLng(")[1].split(")")[0].split(",")
            phone = (
                sp1.select_one("section.section-1")
                .text.split("Call")[1]
                .split("or")[0]
                .strip()
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.text.strip(),
                street_address=addr[0].replace(",", ""),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
