from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("omahasteaks")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val.replace("(", "")
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
    base_url = "https://www.omahasteaks.com/servlet/OnlineShopping?Dsp=2408"
    locator_domain = "https://www.omahasteaks.com/"

    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.vlinks a.storelink")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            if soup1.select_one("a.phonelink"):
                phone = list(soup1.select_one("a.phonelink").stripped_strings)[-1]
            addr = list(
                soup1.select_one("div.ckogroup.no_topborder > div").stripped_strings
            )
            if _p(addr[-1]):
                del addr[-1]
            if "Call" in addr[-1]:
                del addr[-1]
            hours = soup1.find(
                "", string=re.compile(r"Almost all stores", re.IGNORECASE)
            )
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("&storeid=")[1].split("&")[0],
                location_name=link.text.strip(),
                street_address=addr[-2].replace("\n", "").replace("\t", ""),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                phone=phone,
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours.replace(
                    "Almost all stores are now operating", ""
                ).strip(),
                raw_address=" ".join(addr).replace("\n", "").replace("\t", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
