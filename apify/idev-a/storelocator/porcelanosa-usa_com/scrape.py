from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.porcelanosa-usa.com"
base_url = "https://www.porcelanosa-usa.com/us-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("article.locationItem")
        for _ in locations:
            block = list(_.ul.stripped_strings)
            _addr = []
            for aa in block:
                if "Phone" in aa:
                    break
                _addr.append(aa.replace("\n", ""))
            raw_address = " ".join(
                [aa for aa in " ".join(_addr).split(" ") if aa.strip()]
            )
            addr = parse_address_intl(raw_address)
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
            hr = _.find("strong", string=re.compile(r"Store Hours"))
            hours = []
            if hr:
                for hh in hr.find_parent().find_next_siblings():
                    if not hh.text.strip():
                        continue
                    temp = []
                    for tt in hh.stripped_strings:
                        if "Warehouse" in tt or "Showroom" in tt or "OPEN" in tt:
                            continue
                        if "Appointments" in tt:
                            break
                        temp.append(tt)
                    hours.append(" ".join(temp))

            hours_of_operation = "; ".join(hours)
            if hours_of_operation == "By appointment only":
                hours_of_operation = ""

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
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
