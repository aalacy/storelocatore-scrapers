from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("samautoglass")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "http://samautoglass.com/"
    base_url = "https://admin11335.wixsite.com/samautoglass"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = list(soup.select_one("div#comp-jjz14jo510").stripped_strings)
        links += list(soup.select_one("div#comp-jjz14jo515").stripped_strings)
        logger.info(f"{len(links)} found")
        store = []
        for link in links:
            store.append(link)
            if _p(link):
                addr = store[-3:-1]
                yield SgRecord(
                    page_url=locator_domain,
                    location_name=store[0],
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=store[-1],
                    locator_domain=locator_domain,
                )
                store = []


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
