from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.merchantsbankrugby.com"
base_url = "https://www.merchantsbankrugby.com/Locations-Hours"


def _hoo(hours, name):
    for nn, hh in hours.items():
        if name in nn:
            return hh


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        hours = {}
        temp = (
            soup.find("h2", string=re.compile(r"^Hours"))
            .find_next_sibling("table")
            .select("td")
        )
        for hh in temp:
            hr = list(hh.p.stripped_strings)
            if hr and "Lobby" in hr[0]:
                hours[hh.h3.text.replace("Hours", "").strip()] = (
                    hr[0].split("Lobby:")[-1].strip()
                )
        locations = (
            soup.find("h2", string=re.compile(r"^Locations"))
            .find_next_sibling("table")
            .select("td")
        )
        for _ in locations:
            addr = list(_.p.stripped_strings)
            phone = ""
            pp = _.find("", string=re.compile(r"Phone:"))
            if pp:
                phone = list(pp.find_parent().stripped_strings)
                if len(phone) > 1:
                    phone = phone[-1]

            city = " ".join(addr[-1].split()[:-2]).replace(",", "")
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=city,
                state=addr[-1].split()[-2],
                zip_postal=addr[-1].split()[-1],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_hoo(hours, city),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
