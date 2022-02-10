from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.rs"
base_url = "https://www.mcdonalds.rs/restoran-lokator/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .replace("\xa0", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var locations =")[1]
            .split("</script>")[0]
        )
        for _ in locations:
            sp1 = bs(_[3], "lxml")
            raw_address = sp1.p.text.strip()
            addr = parse_address_intl(raw_address + ", Serbia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            phone = ""
            hours = []
            block = []
            for p in (
                sp1.find("strong", string=re.compile(r"Radno vreme restorana"))
                .find_parent()
                .find_next_siblings("p")
            ):
                block += list(p.stripped_strings)
            for x, hh in enumerate(block):
                if _p(hh):
                    phone = hh.replace("\xa0", "")
                    break
            for x, hh in enumerate(block):
                if "Rođendanski" in hh or "Broj parking mesta" in hh or "McDrive" in hh:
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=_[2],
                store_number=_[0],
                location_name=_[1],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_[4],
                longitude=_[5],
                country_code="Serbia",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
