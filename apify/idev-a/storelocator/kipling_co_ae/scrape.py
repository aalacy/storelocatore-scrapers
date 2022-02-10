from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.co.ae"
base_url = "https://www.kipling.co.ae/pages/official-kipling-stores"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table.marketing-table tbody tr")
        for _ in locations:
            td = _.select("td")
            addr = td[2].text.strip().split(",")
            country_code = addr[-1]
            city = ""
            if len(addr) > 1:
                city = addr[0]
            if country_code == "Muscat":
                country_code = "Oman"
                city = "Muscat"
            yield SgRecord(
                page_url=base_url,
                location_name=td[0].text.strip(),
                city=city,
                country_code=country_code,
                phone=td[-1].text.strip(),
                locator_domain=locator_domain,
                raw_address=td[2].text.strip(),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
