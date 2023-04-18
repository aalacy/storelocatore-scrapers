from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.jambajuice.com.tw"
base_url = "http://www.jambajuice.com.tw/store/store.aspx"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#store_box > table")
        for _ in locations:
            lat = _.iframe["src"].split("lat=")[1].split("&")[0]
            lng = _.iframe["src"].split("lng=")[1]
            info = _.table.table.select("tr")
            raw_address = list(info[1].stripped_strings)[1]
            addr = raw_address.split("市")
            hours_of_operation = (
                list(info[3].stripped_strings)[-1]
                .split("】")[-1]
                .replace("\\r\\n", "; ")
                .strip()
            )
            if hours_of_operation.startswith(";"):
                hours_of_operation = hours_of_operation[1:].strip()
            yield SgRecord(
                page_url=base_url,
                location_name=info[0].text.strip(),
                street_address=addr[1],
                city=addr[0] + "市",
                country_code="Taiwan",
                phone=list(info[2].stripped_strings)[-1],
                latitude=lat,
                longitude=lng,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
