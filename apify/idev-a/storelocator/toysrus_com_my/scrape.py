from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toysrus.com.my"
base_url = "https://www.toysrus.com.my/stores/"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _coord(locs, name):
    for loc in locs:
        if loc["name"] == name:
            return loc


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = json.loads(sp1.select_one("div.map-canvas")["data-locations"])
        locations = sp1.select("div.store.store-item")
        for _ in locations:
            raw_address = _["data-store-address1"]
            if _["data-store-address2"]:
                raw_address += ", " + _["data-store-address2"]
            raw_address += (
                ", "
                + _["data-store-city"]
                + ", "
                + _["data-store-statecode"]
                + ", "
                + _["data-store-postalcode"]
            )
            raw_address = raw_address.strip()
            while True:
                if raw_address.endswith(","):
                    raw_address = raw_address[:-1].strip()
                else:
                    break
            addr = parse_address_intl(raw_address + ", Malaysia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hours = []
            temp = {}
            for hh in bs(_["data-store-details"], "lxml").select(
                "div.store-hours div.row"
            ):
                cols = hh.select("div.col-auto")
                temp[cols[0].text.strip()] = " ".join(cols[1].stripped_strings)
            for day in days:
                day = day.lower()
                hours.append(f"{day}: {temp[day]}")

            coord = _coord(locs, _["data-store-name"])

            yield SgRecord(
                page_url=base_url,
                store_number=_["data-store-id"],
                location_name=_["data-store-name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="My",
                latitude=coord["latitude"],
                longitude=coord["longitude"],
                location_type="toysrus",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
