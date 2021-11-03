from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("trencold")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.trencold.com"
base_url = "http://www.trencold.com/warehouses.php"


def _pp(city, phones):
    phone = ""
    for p in phones:
        if city in p:
            phone = p.split("-")[0].strip()
            break
    return phone


streets = []


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.nano-content a")
        logger.info(f"{len(links)} found")
        phones = []
        temp = list(soup.select_one("div#sidebar").stripped_strings)
        for x, pp in enumerate(temp):
            if pp.strip() == "Contact Us.":
                phones = temp[x + 1 :]

        for link in links:
            addr = link.text.split(",")
            street_address = addr[0].split("-")[-1].strip()
            if street_address in streets:
                continue
            streets.append(street_address)
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0].split("-")[0].strip(),
                street_address=street_address,
                city=addr[1].strip(),
                state=addr[2].strip(),
                country_code="CA",
                phone=_pp(addr[1].strip(), phones),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
