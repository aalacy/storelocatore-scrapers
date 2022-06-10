from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://evenstevens.com"
base_url = "https://evenstevens.com/places/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey")[0]
            .strip()[:-1]
        )
        logger.info(f"{len(locations)} found")
        for loc in locations:
            page_url = locator_domain + loc["url"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(
                sp1.select_one('a[data-bb-track-category="Address"]').stripped_strings
            )
            _pp = sp1.select_one('a[data-bb-track-category="Phone Number"]')
            phone = ""
            if _pp:
                phone = _pp.text.strip()
            temp = []
            hours = []
            for hh in sp1.select("section#intro p")[1:]:
                temp.append(hh.text.strip())
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            street_address = " ".join(addr[:-1]).strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=page_url,
                store_number=loc["id"],
                location_name=loc["name"],
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=loc["lat"],
                longitude=loc["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
