from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aabsny")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.aabsny.com/"
    base_url = "https://www.aabsny.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select('div[data-testid="richTextElement"]')
        logger.info(f"{len(links)} found")
        for link in links:
            _text = link.text.strip().lower()
            if "phone" not in _text:
                continue
            if "now open" in _text:
                continue
            addr = [
                aa.strip()
                for aa in link.stripped_strings
                if aa.replace("\u200b", "").strip()
            ]
            phone = addr[4].split(":")[-1].strip().replace("Phone", "")
            if not _p(phone):
                phone = addr[5]
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0],
                street_address=addr[2],
                city=addr[3].split(",")[0].strip(),
                state=addr[3].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[3].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
