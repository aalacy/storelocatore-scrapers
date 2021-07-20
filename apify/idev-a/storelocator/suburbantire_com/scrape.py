from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("suburbantire")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.suburbantire.com"
    base_url = "https://www.suburbantire.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.query--locations > div.col")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.address.stripped_strings)
            if "coming soon" in addr[0].lower():
                continue
            page_url = locator_domain + link.select_one("span.location")["data-link"]
            coord = link.select_one("span.location")["data-location"].split(":")
            yield SgRecord(
                page_url=page_url,
                location_name=link.h3.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=link.select_one("div.phone a").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(
                    link.select_one("div.hours").stripped_strings
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
