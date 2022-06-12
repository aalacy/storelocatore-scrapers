from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("haynesfurniture")

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
    locator_domain = "https://haynesfurniture.com"
    base_url = "https://haynesfurniture.com/Allshops"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.shops-list li.shops-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.a["href"]
            addr = list(link.select_one("div.short-description").stripped_strings)
            phone = addr[2]
            if not _p(phone):
                phone = ""
            hours = [":".join(hh.stripped_strings) for hh in link.select("table tr")]
            yield SgRecord(
                page_url=page_url,
                store_number=link["data-shopid"],
                location_name=link.select_one(".shop-coordinates")["data-shop-title"],
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link.select_one(".shop-coordinates")["data-latitude"],
                longitude=link.select_one(".shop-coordinates")["data-longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
