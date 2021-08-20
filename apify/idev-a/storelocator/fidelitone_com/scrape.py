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


def _filter(val):
    return (
        val.split("var locations =")[1]
        .split("var showAll")[0]
        .strip()[:-1]
        .replace("\n", "")
        .replace("\t", "")
        .replace("\\", "")
        .replace("new google.maps.LatLng(", '"')
        .replace("),", '",')
        .replace("' + '", " ")
    )


def fetch_data():
    with SgRequests() as session:
        links = json.loads(_filter(session.get(base_url, headers=_headers).text))
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + bs(link["title"], "lxml").a["href"].replace(
                " ", "-"
            )
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            locations = json.loads(_filter(res))
            phone = (
                sp1.select_one("section.section-1")
                .text.split("Call")[1]
                .split("or")[0]
                .split("and")[0]
                .strip()
            )
            for _ in locations:
                addr = list(bs(_["title"], "lxml").stripped_strings)
                yield SgRecord(
                    page_url=page_url,
                    location_name=bs(link["title"], "lxml").text.strip(),
                    street_address=addr[0].replace(",", ""),
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=_["position"].split(",")[0].strip(),
                    longitude=_["position"].split(",")[1].strip(),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
