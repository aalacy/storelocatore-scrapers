from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.4fingers.com.sg"
base_url = "https://www.4fingers.com.sg/corp/views/location"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        locations = soup.select("div.outlet-container")
        for _ in locations:
            _addr = []
            for aa in _.select("div.col-xs-10 p"):
                if "Dining" in aa.text or "Delivery" in aa.text:
                    break
                _addr.append(aa.text.strip())

            raw_address = " ".join(_addr)
            _hr = _.find("span", string=re.compile(r"Operation Hours"))
            hours = []
            if _hr:
                for hh in _hr.find_parent("tr").select("td")[-1].select("div span"):
                    if hh.span:
                        continue
                    if "line-through" in hh["style"]:
                        continue
                    hours.append(hh.text.strip())

            _pp = _.find("span", string=re.compile(r"Telephone"))
            phone = ""
            if _pp:
                phone = _pp.find_parent("tr").select("td")[-1].text.strip()
                if phone == "N/A":
                    phone = ""
            name = _.select_one("div.headers-right").text.strip()
            yield SgRecord(
                page_url=base_url,
                location_name=name,
                street_address=" ".join(_addr[:-1]),
                city=_addr[-1].split()[0].strip(),
                zip_postal=_addr[-1].split()[-1].strip(),
                country_code="SG",
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
