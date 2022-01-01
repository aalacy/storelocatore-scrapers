from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.com.vn"
base_url = "https://www.shell.com.vn/motorists/oils-lubricants/distributor-locator.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.text-image__text table tbody tr")[1:]
        for _ in locations:
            raw_address = _.select("td")[2].text.strip()
            addr = parse_address_intl(raw_address + ", Vietnam")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city == "Tp." or city == "Trì":
                for aa in raw_address.split(","):
                    if city.lower() in aa.lower():
                        city = aa
                        break
            yield SgRecord(
                page_url=base_url,
                location_name=_.select("td")[1].text.strip(),
                street_address=street_address.split("Tp.")[0],
                city=city,
                state=addr.state,
                country_code="Vietnam",
                phone=_.select("td")[3].text.split("/")[0].strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
