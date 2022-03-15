from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gabrielsliquor")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://gabrielsliquor.com/"
    base_url = "https://gabrielsliquor.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div.elementor-widget-container article a.elementor-post__thumbnail__link"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(sp1.select("div.elementor-text-editor p")[-1].stripped_strings)
            addr = block[0].split(":")[-1].split(" ")
            zip_postal = addr[-1].strip()
            street_address = " ".join(addr[:-1])
            if not zip_postal.isdigit():
                zip_postal = ""
                street_address = " ".join(addr)
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("h2.elementor-heading-title").text.strip(),
                street_address=street_address,
                zip_postal=zip_postal,
                country_code="US",
                phone=block[2],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
