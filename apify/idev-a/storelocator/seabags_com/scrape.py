from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://seabags.com"
base_url = "https://seabags.com/our-company/visit-us.html"


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
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.row-stores div.store-wrapper"
        )
        for link in locations:
            if "COMING SOON" in link.select_one("div.store-hours h3").text:
                continue
            addr = list(link.select_one(".Store-address").stripped_strings)
            if "@" in addr[-1]:
                del addr[-1]
            phone = _p(addr[-1])
            if phone:
                del addr[-1]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in link.select("div.store-hours div dl")
            ]
            yield SgRecord(
                page_url=base_url,
                location_name=link.h2.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.CITY})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
