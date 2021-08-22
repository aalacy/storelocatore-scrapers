from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("exxpresslube")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _dd(blocks, street):
    latitude = longitude = ""
    for bb in blocks:
        if street in bb.p.text:
            latitude = bb["data-lat"]
            longitude = bb["data-lon"]
            break
    return latitude, longitude


def fetch_data():
    locator_domain = "https://www.exxpresslube.com/"
    base_url = "https://www.exxpresslube.com/locations.html"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container div.container-fluid > div.row > div.col-12")
        blocks = soup.select("div.location")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.select_one("div.row div.col-6 p").stripped_strings)[1:]
            hours = list(link.select("div.row div.col-6")[1].stripped_strings)[1:]
            latitude, longitude = _dd(blocks, addr[0])
            yield SgRecord(
                page_url=base_url,
                location_name=link.h2.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[-1],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
