from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://sbiuk.statebank"
base_url = "https://sbiuk.statebank/branch-location"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.panel")
        for _ in locations:
            aa = list(
                _.select_one(
                    "div.inner-page-content div.inner-row-content"
                ).stripped_strings
            )
            raw_address = aa[-1]
            if "Business Hours:" in aa[0]:
                raw_address = ""
            if not raw_address:
                raw_address = _.h4.text.strip()
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if _.find("strong", string=re.compile(r"Phone")):
                phone = list(
                    _.find("strong", string=re.compile(r"Phone"))
                    .find_parent()
                    .stripped_strings
                )[-1]

            hours = []
            hr = _.find("strong", string=re.compile(r"^Business hours", re.I))
            if not hr:
                hr = _.find("p", string=re.compile(r"^Business hours", re.I))
            if hr:
                hours = list(hr.find_next_sibling().stripped_strings)
                if not hours:
                    hours = list(
                        hr.find_parent("li").find_next_sibling().stripped_strings
                    )

            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
