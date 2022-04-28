from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.familymart.com.my"
base_url = "https://www.familymart.com.my/our-stores.html"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var data =")[1]
            .split("for (var i = 0;")[0]
            .replace("// map data", "")
        )
        for _ in locations:
            info = bs(_["content"], "lxml")
            raw_address = " ".join(info.p.stripped_strings)
            addr = parse_address_intl(raw_address + ", Malaysia")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            zip_postal = addr.postcode
            if not zip_postal:
                zip_postal = raw_address.split(",")[-2].strip().split()[0]
                if not zip_postal.isdigit():
                    zip_postal = ""
                if zip_postal:
                    street_address = street_address.replace(zip_postal, "").strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=" ".join(info.h5.stripped_strings),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="MY",
                latitude=_["position"]["lat"],
                longitude=_["position"]["lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
