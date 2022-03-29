from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.huntbrotherspizza.com"
base_url = "https://api.huntbrotherspizza.com/location/wp_search_result?radius=&order-by%5B%5D=label&order-by%5B%5D=sync_label&near%3A%3C%3D%5Blat%5D=34.043029785156&near%3A%3C%3D%5Blng%5D=-118.25227355957&limit=500&published=true"
page_url = "https://www.huntbrotherspizza.com/locations/"


def fetch_records():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["payload"]
        for _ in locations:
            sp1 = bs(_["popup_content"], "lxml")
            addr = list(sp1.address.stripped_strings)
            phone = ""
            if sp1.select_one("a.phone"):
                phone = sp1.select_one("a.phone").text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["label"].replace("&#039;", "'").replace("&amp;", '"'),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split()[-1].strip(),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for rec in fetch_records():
            writer.write_row(rec)
