from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.aldi.cn"
base_url = "https://www.aldi.cn/aldi/home/en/our-shops/physical-store/index.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.briefList li")
        for _ in locations:
            addr = _.p.text.split(":")[-1].strip()
            hours = (
                _.select("p")[1].text.replace("Opening hours:", "").replace("—", "-")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h1.text.strip(),
                street_address=", ".join(addr.split(",")[:-2]),
                city=addr.split(",")[-1].strip(),
                country_code="CN",
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=addr,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
