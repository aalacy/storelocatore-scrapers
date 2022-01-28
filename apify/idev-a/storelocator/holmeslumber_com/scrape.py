from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.holmeslumber.com"
base_url = "https://www.holmeslumber.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        for table in soup.select("div.std table"):
            if not table.td:
                continue
            locations = table.select("td")
            for _ in locations:
                addr = list(_.strong.stripped_strings)
                block = list(_.stripped_strings)
                phone = ""
                temp = []
                for x, bb in enumerate(block):
                    if "Phone" in bb:
                        phone = bb.replace("Phone:", "").strip()
                    if "Hours" in bb:
                        temp = block[x + 1 :]

                hours = []
                for hh in temp:
                    if "Facebook" in hh:
                        break
                    hr = hh.replace("•", "").strip()
                    if hr:
                        hours.append(hr)
                yield SgRecord(
                    page_url=base_url,
                    location_name=_.h3.text.strip(),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split()[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
