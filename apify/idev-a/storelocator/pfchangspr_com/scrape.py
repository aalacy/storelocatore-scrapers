from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pfchangspr.com"
base_url = "https://www.pfchangspr.com/restaurantes/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.list-of-locations div.single-location > div")
        for _ in locations:
            addr = _.select_one("div.address").text.strip().split(",")
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[:-2]),
                city=addr[-2].strip(),
                state=addr[-1].strip().split()[0].strip(),
                zip_postal=addr[-1].strip().split()[-1].strip(),
                country_code="Puerto Rico",
                phone=list(_.select_one("div.number").stripped_strings)[0],
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation=list(
                    _.select_one("div.store-hours").stripped_strings
                )[1],
                raw_address=", ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
