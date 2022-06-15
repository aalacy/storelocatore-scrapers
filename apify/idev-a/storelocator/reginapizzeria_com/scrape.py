from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

locator_domain = "http://reginapizzeria.com/"
base_url = "http://reginapizzeria.com/"


def _p(val):
    if (
        val
        and val.replace("Phone", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        locations = soup.select("div.dropdown-menu a.dropdown-item")
        for link in locations:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            block = [_ for _ in soup1.select_one("p.mbr-text").stripped_strings]
            phone = ""
            location_type = "<MISSING>"
            addr = []
            street_address = city = state = zip_postal = ""
            if "Menu Items:" in block[0]:
                addr = soup1.iframe["src"].split("&q=")[-1].split(",")
                street_address = " ".join(addr[:-2])
                city = addr[-2].strip()
                state = addr[-1].strip().split()[0].strip()
                zip_postal = addr[-1].strip().split()[-1].strip()
            else:
                for x, bb in enumerate(block):
                    if (
                        "Join us" in bb
                        or "Customers" in bb
                        or "best pizza" in bb
                        or "Please" in bb
                        or "since" in bb
                    ):
                        break
                    if "re-located" in bb or "Pizza" in bb:
                        continue
                    if _p(bb):
                        phone = bb.replace("Phone -", "").strip()
                    else:
                        addr.append(bb)

                if "temporarily closed" in addr[0]:
                    location_type = "Closed"
                    del addr[0]
                if "Regina Pizz" in addr[0]:
                    del addr[0]

                street_address = " ".join(addr[:-1])
                city = addr[-1].split(",")[0].strip()
                state = addr[-1].split(",")[1].strip().split()[0].strip()
                zip_postal = addr[-1].split(",")[1].strip().split()[-1].strip()

            hours = []
            hr = soup1.find("h2", string=re.compile(r"Hours of Operation"))
            if hr:
                hours = list(hr.find_next_sibling().stripped_strings)

            yield SgRecord(
                page_url=page_url,
                location_name=soup1.h1.text.replace("(Relocated)", "").strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
