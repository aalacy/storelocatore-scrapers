from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://chickencottageme.com"
base_url = "https://chickencottageme.com/contact-us/"


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
        locations = soup.select(
            "div#content section div.section-content div.row div.col-inner div.row div.col"
        )
        for _ in locations:
            addr = list(_.p.stripped_strings)
            phone = ""
            if _p(addr[-1]):
                phone = addr[-1]
                del addr[-1]
            if "Phone" in addr[-1]:
                del addr[-1]

            _addr = " ".join(addr).split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=", ".join(_addr[:-2]),
                city=_addr[-2].strip(),
                country_code="United Arab Emirates",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=", ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
