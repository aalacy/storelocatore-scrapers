from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("amwarelogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.amwarelogistics.com"
base_url = "https://www.amwarelogistics.com/fulfillment-warehouses/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.main-menu-list ul li a")[1:]
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if sp1.select("table td"):
                for _ in sp1.select_one("table").select("td"):
                    blocks = list(_.stripped_strings)
                    addr = []
                    phone = ""
                    for x, bb in enumerate(blocks):
                        phone = bb.split(":")[-1].replace("Phone", "").strip()
                        if _p(phone):
                            addr = blocks[:x]
                            break
                        else:
                            phone = ""
                    if not addr:
                        for x, bb in enumerate(blocks):
                            if bb == _.select_one("ul li").text.strip():
                                addr = blocks[:x]
                                break

                    try:
                        yield SgRecord(
                            page_url=page_url,
                            location_name=blocks[0],
                            street_address=addr[-2],
                            city=addr[-1].split(",")[0].strip(),
                            state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                            zip_postal=addr[-1]
                            .split(",")[1]
                            .strip()
                            .split(" ")[-1]
                            .strip(),
                            country_code="US",
                            phone=phone,
                            locator_domain=locator_domain,
                        )
                    except:
                        import pdb

                        pdb.set_trace()
            else:
                blocks = list(
                    sp1.find(
                        "strong",
                        string=re.compile(r"Fulfillment Services &", re.IGNORECASE),
                    )
                    .find_parent()
                    .find_next_sibling()
                    .stripped_strings
                )
                addr = []
                phone = ""
                for x, bb in enumerate(blocks):
                    phone = bb.split(":")[-1].replace("Phone", "").strip()
                    if _p(phone):
                        addr = blocks[:x]
                        break
                    else:
                        phone = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
