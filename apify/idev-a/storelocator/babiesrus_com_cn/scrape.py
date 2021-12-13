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

locator_domain = "https://www.babiesrus.com.cn"
base_url = "https://www.babiesrus.com.cn/en-cn/stores/"
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
            street_address = _["data-store-address1"]
            if _["data-store-address2"]:
                street_address += " " + _["data-store-address2"]
            street_address = (
                street_address.replace("Ganzhou", "Guangzhou")
                .replace("Shang Ha", "Shanghai")
                .replace("’", "'")
            )
            if "shenzhen" not in street_address and "shenzhe" in street_address:
                street_address = street_address.replace("shenzhe", "shenzhen")
            if "Beijing" not in street_address and "Beijn" in street_address:
                street_address = street_address.replace("Beijn", "Beijing")
            raw_address = street_address.strip()
            addr = parse_address_intl(raw_address + ", China")
            city = (
                _["data-store-city"]
                .replace("’", "'")
                .replace("Ji'nan", "Jinan")
                .replace("Ganzhou", "Guangzhou")
            )
            if "Haidian district of" not in street_address:
                x = street_address.lower().rfind(city.lower())
                street_address = street_address[:x].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            hours = []
            temp = {}
            for hh in bs(_["data-store-details"], "lxml").select(
                "div.store-hours div.row"
            ):
                cols = hh.select("div.col-auto")
                temp[cols[0].text.strip()] = " ".join(cols[1].stripped_strings)
            for day in days:
                day = day.lower()
                times = "closed"
                if temp.get(day):
                    times = temp.get(day)
                hours.append(f"{day}: {times}")

            coord = _coord(locs, _["data-store-name"])
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-store-id"],
                location_name=_["data-store-name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=_["data-store-postalcode"],
                country_code="China",
                latitude=coord["latitude"],
                longitude=coord["longitude"],
                location_type="babiesrus",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
