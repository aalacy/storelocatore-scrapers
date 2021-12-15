from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.chickendelight.com"
base_url = "https://www.chickendelight.com/wp-admin/admin-ajax.php?action=getlocations&lat=0&lng=0"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["loc"]
        for _ in locations:
            raw_address = (
                " ".join(bs(_["a"], "lxml").stripped_strings)
                .replace("&nbsp;", " ")
                .replace("&#8217;", "'")
            )
            if "Canada" not in raw_address:
                raw_address += ", Canada"
            addr = parse_address_intl(raw_address)
            hours = []
            hr = list(bs(_["h"], "lxml").stripped_strings)
            if hr:
                for hh in hr[1:]:
                    if "Holiday" in hh or "Delivery" in hh:
                        break

                    if "Hour" in hh:
                        continue
                    hours.append(hh)
            yield SgRecord(
                page_url=_["url"],
                store_number=_["id"],
                location_name=raw_address,
                street_address=_["t"]
                .replace("&nbsp;", " ")
                .replace("&#8217;", "'")
                .split("(")[0]
                .strip(),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="CA",
                phone=_["p"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
