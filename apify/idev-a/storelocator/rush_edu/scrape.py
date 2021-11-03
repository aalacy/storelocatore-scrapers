from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("rush")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.rush.edu"
    base_url = "https://www.rush.edu/locations?page={}"
    with SgRequests() as session:
        page = 0
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.locations-search--results-wrap div.location-card")
            if not links:
                break
            logger.info(f"[page {page}] {len(links)} found")
            page += 1
            for link in links:
                page_url = locator_domain + link.a["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = list(link.p.stripped_strings)
                hours = [
                    "".join(hh.stripped_strings)
                    .split("(")[0]
                    .split("Dates")[0]
                    .split("Call")[0]
                    for hh in link.select("div.office-hours__item")
                ]
                coord = (
                    sp1.select_one("div.location-address img")["src"]
                    .split("/400x225")[0]
                    .split("/")[-1]
                    .split(",")
                )
                _phone = link.find("a", href=re.compile(r"tel:"))
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.h3.text.strip().replace("–", "-"),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=_phone.text.strip() if _phone else "",
                    locator_domain=locator_domain,
                    latitude=coord[1],
                    longitude=coord[0],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
