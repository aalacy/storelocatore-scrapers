from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("salutbaramericain")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://salutbaramericain.com/"
base_url = "https://salutbaramericain.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select('a[title="Location & Hours"]')
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.get("href")
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = (
                " ".join(
                    [
                        p.text.strip()
                        for p in sp1.select("div.entry-content p")
                        if p.text.strip()
                    ]
                )
                .replace("–", ",")
                .split(",")
            )
            hours = []
            for hh in (
                sp1.find("strong", string=re.compile(r"Hours of Operation"))
                .find_parent()
                .find_next_siblings("div")
            ):
                if not hh.text.strip():
                    continue
                if "RESERVATIONS" in hh.text:
                    break
                hours.append(" ".join(hh.stripped_strings))
            if "Daily" in hours[-1]:
                del hours[-1]
            coord = (
                sp1.select_one("div.gmap iframe")["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3d")
            )
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.entry-content h1").text.strip(),
                street_address=addr[0].replace("50th and France", "").strip(),
                city=addr[1].strip(),
                state=addr[2].strip().split(" ")[0].strip(),
                zip_postal=addr[2].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
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
