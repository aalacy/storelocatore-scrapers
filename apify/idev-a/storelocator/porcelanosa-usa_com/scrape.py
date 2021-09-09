from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
base_url = "https://www.porcelanosa-usa.com/us-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("article.locationItem")
        for _ in locations:
            block = list(_.ul.stripped_strings)
            raw_address = []
            for aa in block:
                if "Phone" in aa:
                    break
                raw_address.append(aa.replace("\n", ""))
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            country_code = "US"
            if len(addr.postcode) > 5:
                country_code = "CA"
            state = addr.state
            if not state:
                state = _.h4.text.split(",")[-1].strip()
            phone = ""
            if _.select_one("li a"):
                phone = _.select_one("li a").text.strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"].split("-")[-1],
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
