from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.americancarcenter.com"
base_url = "https://www.americancarcenter.com/locations-at-american-car-center"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        sp1 = bs(
            soup.select_one("a.header-contact__link.js-location")["data-content"],
            "lxml",
        )
        markers = sp1.img["data-src"].split("&markers=size:small|")[1:]
        locations = sp1.select("div.get-direction__dealer")
        for x, _ in enumerate(locations):
            raw_address = (
                _.select_one("div.get-direction__dealer-name")
                .find_next_sibling()
                .text.strip()
            )
            addr = raw_address.split(",")
            try:
                phone = (
                    _.select_one("div.get-direction__dealer-name")
                    .find_next_sibling()
                    .find_next_sibling()
                    .text.strip()
                )
            except:
                phone = ""
            marker = markers[x].split("%2C")
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-id"],
                location_name=_.select_one(
                    "div.get-direction__dealer-name"
                ).text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                state=addr[-1].split()[0].strip(),
                zip_postal=addr[-1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=marker[0],
                longitude=marker[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
