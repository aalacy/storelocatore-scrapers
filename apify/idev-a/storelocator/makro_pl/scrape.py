from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.pl/"
urls = {
    "Poland": {
        "base_url": "https://www.makro.pl/services/StoreLocator/StoreLocator.ashx?id={91546E5B-E850-482B-9772-85D8EC00BC7C}&lat=52.44&lng=19.4&language=pl-PL&distance=150000000&limit=100",
    },
    "Czech": {
        "base_url": "https://www.makro.cz/services/StoreLocator/StoreLocator.ashx?id={13FDC359-A2FA-4FBF-88EB-4B7563B5CF56}&lat=50.109901&lng=14.574037&language=cs-CZ&distance=350000&limit=100",
    },
}

base_pt = "https://www.makro.pt/Lojas"
url_pt = "https://www.makro.pt//sxa/search/results/?itemid={732FAE99-1581-4F71-BC3C-D423B5A1AF24}&sig=store-locator&g=%7C&o=StoreName%2CAscending&p=20&v=%7BA0897F25-35F9-47F8-A28F-94814E5A0A78%7D&limit=100"
json_pt = "https://www.makro.pt//sxa/geoVariants/657adfba-e18f-49e6-90f9-aa9bb0a8ae4a/{}/39.4699075,-0.3762881/undefined"


def _pp(locs, name):
    for loc in locs:
        if loc.select_one("div.store-name").text.strip() == name:
            return loc.select_one("div.store-phone").text.strip()


def fetch_data():
    with SgRequests() as session:
        for country, url in urls.items():
            logger.info(url)
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

        logger.info(url_pt)
        locs = bs(session.get(base_pt, headers=_headers).text, "lxml").select(
            "div.store-details"
        )
        locations = session.get(url_pt, headers=_headers).json()["Results"]
        for _ in locations:
            html = session.get(json_pt.format(_["Id"]), headers=_headers).json()
            info = bs(html["Html"], "lxml")
            raw_address = info.select_one("div.sl-address").text.strip()
            addr = raw_address.split(",")
            hours = []
            temp = info.select_one("div.sl-opening-hours").findChildren(recursive=False)
            day = time = ""
            for hh in temp:
                if "field-translation" in hh.get("class", []):
                    day = hh.text.strip()
                if "field-hours-for-customer-type-1" in hh.get("class", []):
                    time = hh.text.strip()
                if hh.name == "br":
                    hours.append(f"{day}: {time}")
                    day = time = ""
            location_name = info.select_one("div.sl-store-name").text.strip()
            yield SgRecord(
                page_url=base_pt,
                location_name=location_name,
                street_address=", ".join(addr[:-2]),
                city=addr[-2],
                zip_postal=addr[-1],
                country_code="Portugal",
                phone=_pp(locs, location_name),
                latitude=_["Geospatial"]["Latitude"],
                longitude=_["Geospatial"]["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
