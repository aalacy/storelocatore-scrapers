from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.huntbrotherspizza.com"
base_url = "https://api.huntbrotherspizza.com/location/wp_search_result?radius=&order-by%5B%5D=label&order-by%5B%5D=sync_label&near%3A%3C%3D%5Blat%5D={}&near%3A%3C%3D%5Blng%5D={}&limit=500&published=true"
page_url = "https://www.huntbrotherspizza.com/locations/"


def fetch_records(search):
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "payload"
            ]
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                search.found_location_at(_["latitude"], _["longitude"])
                sp1 = bs(_["popup_content"], "lxml")
                addr = list(sp1.address.stripped_strings)
                phone = ""
                if sp1.select_one("a.phone"):
                    phone = sp1.select_one("a.phone").text.strip()
                try:
                    yield SgRecord(
                        page_url=page_url,
                        store_number=_["id"],
                        location_name=_["label"]
                        .replace("&#039;", "'")
                        .replace("&amp;", '"'),
                        street_address=addr[0],
                        city=addr[1].split(",")[0].strip(),
                        state=addr[1].split(",")[1].strip().split()[0].strip(),
                        zip_postal=addr[1].split(",")[1].strip().split()[-1].strip(),
                        latitude=_["latitude"],
                        longitude=_["longitude"],
                        country_code="US",
                        phone=phone,
                        locator_domain=locator_domain,
                        raw_address=" ".join(addr),
                    )
                except Exception as err:
                    print(err)
                    import pdb

                    pdb.set_trace()


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=1000
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
