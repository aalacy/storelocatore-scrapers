from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch

logger = SgLogSetup().get_logger("cottonon")

locator_domain = "https://cottonon.com/"
base_url = "https://cottonon.com/US/store-finder/"
store_url = (
    "https://cottonon.com/on/demandware.store/Sites-cog-us-Site/en_US/Stores-FindStores"
)

_headers = {
    "accept": "text/plain, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://cottonon.com",
    "referer": "https://cottonon.com/US/store-finder/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _data(token, country, lat, lng):
    return {
        "dwfrm_storelocator_brandsInStore": "CottonOn,CottonOnBody,RubiShoes,CottonOnKids,Typo",
        "dwfrm_storelocator_country": country,
        "dwfrm_storelocator_textfield": "",
        "csrf_token": token,
        "format": "ajax",
        "lat": str(lat),
        "lng": str(lng),
        "dwfrm_storelocator_findByLocation": "x",
    }


def fetch_data(search, http):
    for lat, lng in search:
        soup = bs(http.get(base_url, headers=_headers).text, "lxml")
        token = soup.select_one("input[name='csrf_token']")["value"]
        country = search.current_country()
        sp1 = bs(
            http.post(
                store_url, headers=_headers, data=_data(token, country, lat, lng)
            ).text,
            "lxml",
        )
        locations = sp1.select("div.store-details")
        logger.info(f"[{country}] {len(locations)} found")
        for _ in locations:
            hours = []
            for hh in _.select("div.opening-hours .store-hours"):
                time = hh.select("div")[1].text.strip()
                if time == "-":
                    time = "Closed"
                hours.append(f"{hh.select('div')[0].text.strip()} {time}")
            coord = _.select_one("a.view-map-link")["href"].split("?q=")[1].split(",")
            location_type = _.select_one("div.store-brand").text.strip()
            phone = _.select_one("div.store-phone a").text.strip()
            if phone in ["NA", "TBA", "TBD"]:
                phone = ""
            page_url = f"https://cottonon.com/US/store-finder/store-details//?StoreID={_['data-id']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["data-id"],
                location_name=_.h2.text.strip(),
                street_address=_.select_one("div.store-address1").text.strip(),
                city=_.select_one("div.store-city").text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=_.select_one("div.store-postalCode").text.strip(),
                country_code=_.select_one("div.store-countryCodeValue").text.strip(),
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("(Today)", ""),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        with SgRequests() as http:
            countries = []
            for country in bs(http.get(base_url, headers=_headers).text, "lxml").select(
                "select.storelocator-country-select option "
            ):
                cc = country["value"].lower()
                if cc == "hk":
                    cc = "cn"
                countries.append(cc)
            search = DynamicGeoSearch(
                country_codes=list(set(countries)), expected_search_radius_miles=500
            )
            results = fetch_data(search, http)
            for rec in results:
                writer.write_row(rec)
