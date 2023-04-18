from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kempsvillebuilding.com"
base_url = "https://www.kempsvillebuilding.com/locations"


def _p(val):
    if (
        val
        and val.replace("(", "")
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
        for table in soup.find(
            "h2", string=re.compile(r"^Store Locations")
        ).find_next_siblings("table"):
            locations = table.select("td")
            for _ in locations:
                if not _.text.strip():
                    continue
                block = list(_.stripped_strings)[2:]
                addr = []
                phone = ""
                hours = ""
                for x, bb in enumerate(block):
                    if _p(bb):
                        phone = bb
                        addr = block[:x]
                    if "Store Hours" in bb:
                        hours = block[x + 1]

                yield SgRecord(
                    page_url=base_url,
                    location_name=_.strong.text.strip(),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split()[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=" ".join(addr),
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
