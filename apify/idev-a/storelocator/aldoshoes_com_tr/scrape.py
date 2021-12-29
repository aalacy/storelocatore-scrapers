from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.aldoshoes.com.tr"
base_url = "https://www.aldoshoes.com.tr/magazalar"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.StoreLocate div.col-md-12")[:-1]
        for _ in locations:
            block = list(_.stripped_strings)
            if "Tel" in block[-1]:
                phone = block[-1].split(":")[-1].strip()
                del block[-1]
            addr = block[2:]
            city = addr[-1].split("-")[-1]
            street_address = " ".join(addr[:-1]) + addr[-1].split("-")[0]
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=city,
                country_code="Turkey",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=block[1].replace("Çalışma Saatleri:", ""),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
