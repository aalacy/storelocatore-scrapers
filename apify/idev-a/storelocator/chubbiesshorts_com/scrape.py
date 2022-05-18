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
locator_domain = "https://www.chubbiesshorts.com/"
base_url = "https://www.chubbiesshorts.com/pages/stores"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            'div[data-builder-component="page"] > div > div > div'
        )[1:-1]
        for loc in locations:
            _ = loc.findChildren(recursive=False)[1].findChildren(recursive=False)
            hours = []
            days = list(_[1].span.stripped_strings)
            times = list(_[1].select("span")[1].stripped_strings)
            for x in range(len(days)):
                hours.append(f"{days[x]}: {times[x]}")
            phone = ""
            if loc.find("a", href=re.compile(r"tel:")):
                phone = loc.find("a", href=re.compile(r"tel:")).text.strip()
            coord = (
                loc.select("a.builder-block")[-1]["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
            addr = list(_[2].span.stripped_strings)
            yield SgRecord(
                page_url=base_url,
                location_name=loc.p.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
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
