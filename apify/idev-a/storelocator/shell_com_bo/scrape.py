from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.com.bo"
base_url = "https://www.shell.com.bo/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.text-image__text")[1].select("p")
        for _ in locations:
            block = list(_.stripped_strings)
            _addr = []
            phone = ""
            for x, aa in enumerate(block):
                if "Tel" in aa:
                    phone = aa.split(":")[-1].strip()
                    _addr = block[:x]
                    break
            yield SgRecord(
                page_url=base_url,
                location_name=_.find_previous_sibling("h3").text.strip(),
                street_address=" ".join(_addr[:-1]),
                city=_addr[-1].split(",")[0].strip(),
                country_code="Bolivia",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
