from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.servisfirstbank.com"
base_url = "https://www.servisfirstbank.com/Locations"


def fetch_data():
    with SgRequests() as http:
        links = bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "table.Table-Location"
        )
        for _ in links:
            addr = list(
                _.find("h4", string=re.compile(r"Address"))
                .find_next_sibling()
                .stripped_strings
            )
            _hr = _.find("", string=re.compile(r"Lobby Hours"))
            hours = []
            if _hr:
                for hh in list(
                    _hr.find_parent("h4").find_next_sibling().stripped_strings
                ):
                    if "Lunch" in hh:
                        break
                    if "drive" in hh:
                        break
                    hours.append(hh)
            location_type = "branch"
            if _.select("em") and "ATM" in _.select("em")[-1].text:
                location_type += ",atm"
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=base_url,
                location_name=_.find_previous_sibling().text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
