from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(val):
    return (
        val.replace(")", "")
        .replace("(", "")
        .replace("-", "")
        .replace(" ", "")
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://diyhomecenter.net/"
    base_url = "https://diyhomecenter.net/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("li.menu-item-184 ul.g-dropdown li ul li.g-menu-item a")
        for link in links:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            addr = list(soup1.select_one("div#custom-5926-particle").stripped_strings)
            block = list(soup1.select_one("div#custom-9810-particle").stripped_strings)
            phone = ""
            if _phone(addr[-1]):
                phone = addr[-1]
            if _phone(block[0]):
                phone = block[0]
            yield SgRecord(
                page_url=link["href"],
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2].split(",")[0].strip(),
                state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
