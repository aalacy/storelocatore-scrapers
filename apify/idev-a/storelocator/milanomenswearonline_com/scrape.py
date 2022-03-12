from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("milanomenswearonline")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://milanomenswearonline.com"
base_url = "https://milanomenswearonline.com/"


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
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("footer div.desktop-4")[1].select("ul li")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = [
                bb.text.strip()
                for bb in sp1.select_one("div#page").findChildren(recursive=False)
                if bb.text.strip()
            ]
            addr = hours = []
            phone = ""
            for x, bb in enumerate(block):
                if _p(bb):
                    phone = bb
                    addr = block[:x]
                    hours = block[x + 1 :]
                    break
            if hours and "Hour" in hours[0]:
                del hours[0]
            street_address = (
                " ".join(addr[:-1])
                .split("Menswear")[-1]
                .split("CENTER")[-1]
                .replace("WOLFCHASE GALLERIA", "")
                .strip()
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.text.strip(),
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr)
                .split("Menswear")[-1]
                .split("CENTER")[-1]
                .replace("WOLFCHASE GALLERIA", "")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
