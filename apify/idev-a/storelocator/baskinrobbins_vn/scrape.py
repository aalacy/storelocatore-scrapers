from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://baskinrobbins.vn"
base_url = "https://baskinrobbins.vn/vn/index/he-thong-cua-hang"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#resultsDiv")
        for _ in locations:
            addr = _.select_one("div.storeInfo p").text.split(":")[-1]
            hours = ": ".join(
                [
                    hh.text.strip()
                    for hh in _.select("div.storeInfo p")[1:]
                    if hh.text.strip()
                ]
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                store_number=_.select_one("div.index").text.strip(),
                street_address=addr,
                city="TP Hồ Chí Minh",
                country_code="Vietnam",
                locator_domain=locator_domain,
                hours_of_operation=hours,
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
