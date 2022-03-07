from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.openinghours-shops.com"
base_url = "https://www.openinghours-shops.com/en/store/Belgium/shopping%20center?rows=50&page={}"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            locations = bs(
                session.get(base_url.format(page), headers=_headers).text, "lxml"
            ).select("section.vestigingen div.section-inner ul li")
            if not locations:
                break
            page += 1
            for _ in locations:
                try:
                    page_url = locator_domain + _.a["href"]
                except:
                    continue
                logger.info(page_url)
                sp1 = bs(
                    session.get(page_url.format(page), headers=_headers).text,
                    "lxml",
                )
                addr = list(_.select_one("div.vestiging-info-adres").stripped_strings)
                hours = []
                day = ""
                for hh in sp1.select("table.openingsuren tr"):
                    if hh.select_one("td.day"):
                        day = list(hh.select_one("td.day").stripped_strings)[0]

                    hours.append(f"{day}: {hh.select_one('td.open').text.strip()}")

                phone = ""
                if sp1.select_one("table.details").find("a", href=re.compile(r"tel:")):
                    phone = (
                        sp1.select_one("table.details")
                        .find("a", href=re.compile(r"tel:"))
                        .text.strip()
                    )
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.h3.text.strip(),
                    street_address=addr[0],
                    city=" ".join(addr[1].split()[1:]),
                    zip_postal=addr[1].split()[0],
                    country_code="Belgium",
                    phone=phone,
                    location_type=_.select_one(
                        "div.vestiging-info-categorie"
                    ).text.strip(),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
