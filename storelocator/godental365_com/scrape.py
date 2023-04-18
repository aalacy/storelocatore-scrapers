from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.godental365.com"
base_url = "https://www.godental365.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.marker")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = sp1.select_one("div.address-container").text.strip()
            addr = parse_address_intl(raw_address + ", United States")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.isdigit():
                street_address = raw_address.split(",")[0]

            city = addr.city
            if not city:
                if "Brooklyn" in raw_address or "Bronx" in raw_address:
                    city = "New York City"

            hours = [
                " ".join(hh.stripped_strings)
                for hh in sp1.select("ul.operation-container li")
            ]
            phone = ""
            if sp1.select_one("div#maincontent div.telephone-container"):
                phone = sp1.select_one(
                    "div#maincontent div.telephone-container"
                ).text.strip()

            yield SgRecord(
                page_url=page_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
