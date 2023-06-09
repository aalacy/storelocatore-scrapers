from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://caliburger.com"
    base_url = "https://caliburger.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locations-block div#us-accordion")
        for _ in locations:
            prev = _.find_previous_sibling("div", class_="cali-country")
            if prev:
                if "cali-country" in prev.get("class", []):
                    if prev.text != "United States":
                        break
            location_name = _.select_one("div.cali-store-name td").text.strip()
            if re.search(r"coming soon", location_name, re.IGNORECASE):
                continue
            page_url = ""
            if _.select_one("div.cali-store-name a"):
                page_url = (
                    locator_domain + _.select_one("div.cali-store-name a")["href"]
                )
            raw_address = " ".join(
                [dd.text for dd in _.select("div.cali-store-address")]
            )
            addr = parse_address_intl(raw_address)
            coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord[1],
                longitude=coord[0],
                zip_postal=addr.postcode,
                country_code="US",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
