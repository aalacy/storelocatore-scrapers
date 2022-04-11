from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.nalleyfresh.com"
base_url = "https://www.nalleyfresh.com/locations.php"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#locations  div.medium-up-2 div.column")
        for _ in links:
            page_url = locator_domain + _.a["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = _.select_one("div.address").text.strip()
            addr = parse_address_intl(raw_address + ", United States")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _phone = sp1.select_one("div.phone")
            phone = ""
            if _phone:
                phone = list(_phone.stripped_strings)[-1]

            hours = []
            _hr = sp1.select_one("div.hours")
            if _hr:
                hours = list(_hr.stripped_strings)[1:]

            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
