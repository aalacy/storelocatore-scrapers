from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.bg"
base_url = "https://mcdonalds.bg/en/map/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers), "lxml").select(
            "div.restaurant-info"
        )
        for _ in locations:
            addr = list(_.p.stripped_strings)
            if "Tel" in addr[-1]:
                del addr[-1]
            if "map" in addr[-1]:
                del addr[-1]
            street_address = " ".join(addr).split("(")[0].split("Tel.")[0].strip()
            if street_address.endswith("–") or street_address.endswith(","):
                street_address = street_address[:-1]
            pp = _.find("", string=re.compile(r"Tel."))
            phone = ""
            if pp:
                phone = pp.split("Tel.")[-1].split("Tel:")[-1].strip()
            hours = []
            blocks = list(_.stripped_strings)
            for x, hh in enumerate(blocks):
                if "Opening hours" in hh:
                    for hr in blocks[x + 1 :]:
                        if hr == ":":
                            continue
                        _hr = hr.lower()
                        if "delivery" in _hr or "due" in _hr or "mccafe" in _hr:
                            break
                        hours.append(hr)
                    break

            yield SgRecord(
                page_url="https://mcdonalds.bg/en/map/",
                store_number=_["data-post_id"],
                location_name=_.h3.text.strip(),
                street_address=street_address.split("/")[0],
                city=_["data-city_title"],
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                country_code="BG",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("Opening hours:", "")
                .replace("Opening hours", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
