from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

logger = SgLogSetup().get_logger("rostituscankitchen_com")


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.rostituscankitchen.com/"
        base_url = "https://www.rostituscankitchen.com/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("section")[1].select("div.elementor-button-wrapper a")
        for link in links:
            if not link.get("href", "").startswith("https"):
                break
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            block = soup1.select("div.elementor-widget-container ul li")
            addr = parse_address_intl(" ".join(list(block[0].stripped_strings)))
            logger.info(link["href"])
            yield SgRecord(
                page_url=link["href"],
                location_name=link.text.strip(),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[1].text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
