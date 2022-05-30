from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger("baskinrobbins")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://baskinrobbins.com.au"
base_url = "https://baskinrobbins.com.au/store-locator/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select("div.list-search")
        for state in states:
            locations = state.select("div.list")
            st = state.find_previous_sibling("h2").text.strip()
            for _ in locations:
                location_name = _.h3.text.split("–")[0].split("-")[0].strip()
                if "soon" in location_name.lower():
                    continue
                hours_of_operation = ""
                if "temporarily closed" in location_name.lower():
                    hours_of_operation = "Temporarily Closed"
                raw_address = (
                    " ".join([p.text for p in _.select("p")])
                    .replace("\n", "")
                    .replace("\t", " ")
                    .replace("\r", " ")
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                if not city:
                    city = location_name.split(",")[0].strip()
                phone = ""
                if _.select_one("div.phone"):
                    phone = _.select_one("div.phone").text.strip()
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=st,
                    zip_postal=addr.postcode,
                    country_code="AU",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.CITY, SgRecord.Headers.PHONE, SgRecord.Headers.ZIP}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
