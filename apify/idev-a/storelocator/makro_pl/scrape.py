from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("makro")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.pl/"
urls = {
    "Poland": {
        "base_url": "https://www.makro.pl/services/StoreLocator/StoreLocator.ashx?id={91546E5B-E850-482B-9772-85D8EC00BC7C}&lat=52.44&lng=19.4&language=pl-PL&distance=150000000&limit=100",
    },
    "Czech": {
        "base_url": "https://www.makro.cz/services/StoreLocator/StoreLocator.ashx?id={13FDC359-A2FA-4FBF-88EB-4B7563B5CF56}&lat=50.109901&lng=14.574037&language=cs-CZ&distance=350000&limit=16",
    },
    "Portugal": {
        "base_url": "https://www.makro.pt/services/StoreLocator/StoreLocator.ashx?id={312053CC-BCFB-4F75-83AE-6C73FD6C0E03}&lat=40.243584&lng=-8.43352&language=pt-PT&distance=10000000&limit=16",
    },
}


def fetch_data():
    with SgRequests() as session:
        for country, url in urls.items():
            locations = session.get(url["base_url"], headers=_headers).json()["stores"]
            for _ in locations:
                hours = []
                for hh in _["openinghours"].get("all", []):
                    hours.append(f"{hh['title']}: {hh['hours']}")
                zip_postal = []
                for zz in _["zip"]:
                    if zz.isdigit() or zz == "-" or zz == " ":
                        zip_postal.append(zz)
                yield SgRecord(
                    page_url=_["link"],
                    location_name=_["name"],
                    street_address=_["street"],
                    city=_["city"],
                    zip_postal="".join(zip_postal),
                    country_code=country,
                    phone=_["telnumber"],
                    latitude=_["lat"],
                    longitude=_["lon"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
