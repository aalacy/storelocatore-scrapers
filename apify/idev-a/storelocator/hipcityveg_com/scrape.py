from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://hipcityveg.com/"
base_url = "https://hipcityveg.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locations li.store-location")
        for _ in locations:
            addr = list(_.select(".store-info .block")[0].stripped_strings)
            street_address = _.select_one("span.address").text.strip()
            if "DELIVERY ONLY" in addr[-1] or "DELIVERY ONLY" in addr[0]:
                continue
            block = list(_.select(".store-info .block")[1].stripped_strings)
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=street_address,
                street_address=street_address,
                city=_.select_one("span.city").text.strip()
                if _.select_one("span.city")
                else "",
                state=_.select_one("span.state").text.strip()
                if _.select_one("span.state")
                else "",
                zip_postal=_.select_one("span.zip").text.strip()
                if _.select_one("span.zip")
                else "",
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                country_code="US",
                phone=block[0],
                hours_of_operation="; ".join(block[1:]),
                locator_domain=locator_domain,
                raw_address=", ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
