from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("supermacs")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://supermacs.ie"
base_url = "https://supermacs.ie/wp-admin/admin-ajax.php?action=get_markers&address=&distance=5"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["markers"]
        for _ in locations:
            addr = list(bs(_["store_address"], "lxml").stripped_strings)
            hours = []
            if _["store_opening_hours"] and bs(_["store_opening_hours"], "lxml").table:
                trs = (
                    bs(_["store_opening_hours"], "lxml")
                    .select("table#store-schedule")[0]
                    .select("tr")
                )
                days = list(trs[0].stripped_strings)
                start = list(trs[1].stripped_strings)
                end = list(trs[-1].stripped_strings)
                for x in range(len(days)):
                    hours.append(f"{days[x]}: {start[x]} - {end[x]}")
            c_idx = -2
            zip_postal = addr[-1].strip()
            if zip_postal.startswith("Co."):
                zip_postal = ""
            if len(zip_postal.split()) == 1 or zip_postal == "Portlaoise":
                zip_postal = ""
                c_idx += 1
            if addr[-2].strip().startswith("Co."):
                c_idx -= 1
            city = addr[c_idx].replace(",", "").strip()
            street_address = " ".join(addr[:c_idx]).strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=_["store_link"],
                location_name=_["location"]
                .replace("&#8211;", "'")
                .replace("&#8217;", "'"),
                street_address=street_address,
                city=city.replace(",", ""),
                zip_postal=zip_postal,
                latitude=_["store_latitude"],
                longitude=_["store_longitude"],
                country_code="Ireland",
                phone=_["store_telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr).replace("\n", "").replace("\r", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
