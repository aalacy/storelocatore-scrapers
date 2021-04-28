from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("budgetinn")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.budgetinn.com/"
    base_url = "http://www.budgetinn.com/sitemap.html"
    with SgRequests() as session:
        while True:
            res = session.get(base_url, headers=_headers)
            if res.status_code != 200:
                break
            soup = bs(res.text, "lxml")
            links = soup.select("table td a")
            logger.info(f"{len(links)} found")
            for link in links:
                if "Prev" in link.text:
                    continue
                if "Next" in link.text:
                    continue
                page_url = locator_domain + link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                if not sp1.select_one(".addrs"):
                    continue
                addr = list(sp1.select_one(".addrs").stripped_strings)
                country_code = addr[-1].split(",")[-1].strip()
                if not addr[-1]:
                    continue
                elif "us" in addr[-1].lower():
                    country_code = "Us"
                elif "ca" in addr[-1].lower():
                    country_code = "Ca"
                else:
                    continue
                street_address = addr[0]
                if len(addr) == 2:
                    street_address = ""
                city = addr[-2].split("-")[0].strip()
                zip_postal = addr[-2].split("-")[-1].strip()
                if country_code == "Us":
                    zip_postal = zip_postal.split(" ")[-1]
                state = addr[-1].split(",")[0].strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.select_one("h2.head").text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    locator_domain=locator_domain,
                )

            next_link = soup.find("a", string=re.compile(r"Next"))
            if not next_link:
                break
            base_url = locator_domain + next_link["href"]
            logger.info(f"[SITEMAP *****] {base_url}")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
