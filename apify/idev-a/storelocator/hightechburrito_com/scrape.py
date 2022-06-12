from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://hightechburrito.com/"
base_url = "http://hightechburrito.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("section > div.spw-content")[1:]
        for link in links:
            block = []
            for bb in link.select("h4"):
                block += list(bb.stripped_strings)
            addr = []
            hours = []
            temp = []
            phone = ""
            for x, bb in enumerate(block):
                if bb == "PHONE":
                    addr = block[:x]
                    phone = block[x + 1]
                if bb == "HOURS":
                    temp = block[x + 1 :]
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]}: {temp[x+1]}")

            coord = link.select_one("div.ly-element-map > div")
            yield SgRecord(
                page_url=base_url,
                location_name=link.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=coord["data-latitude"],
                longitude=coord["data-longitude"],
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
