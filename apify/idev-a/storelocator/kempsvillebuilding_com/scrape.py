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
base_url = "https://www.kempsvillebuilding.com/#"


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
            "h3", string=re.compile(r"^Kempsville Locations")
        ).find_next_siblings("table"):
            locations = table.select("td")
            for _ in locations:
                block = list(_.stripped_strings)
                addr = block[1:]
                phone = ""
                if _p(addr[-1]):
                    phone = addr[-1]
                    del addr[-1]

                yield SgRecord(
                    page_url=base_url,
                    location_name=block[0],
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split()[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
