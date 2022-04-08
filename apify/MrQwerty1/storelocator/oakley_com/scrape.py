from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    apis = [
        {
            "api": "https://www.oakley.com/en-jp/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.JAPAN],
        },
        {
            "api": "https://www.oakley.com/en-au/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.AUSTRALIA],
        },
        {
            "api": "https://www.oakley.com/en-gb/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.BRITAIN],
        },
        {
            "api": "https://www.oakley.com/de-ch/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.SWITZERLAND],
        },
        {
            "api": "https://www.oakley.com/en-se/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.SWEDEN],
        },
        {
            "api": "https://www.oakley.com/es-es/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.SPAIN],
        },
        {
            "api": "https://www.oakley.com/en-eu/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [
                SearchableCountries.SLOVENIA,
                SearchableCountries.SLOVAKIA,
                SearchableCountries.MALTA,
                SearchableCountries.LITHUANIA,
                SearchableCountries.LATVIA,
                SearchableCountries.GREECE,
                SearchableCountries.FINLAND,
                SearchableCountries.ESTONIA,
                SearchableCountries.CYPRUS,
            ],
        },
        {
            "api": "https://www.oakley.com/en-pt/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.PORTUGAL],
        },
        {
            "api": "https://www.oakley.com/en-pl/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.POLAND],
        },
        {
            "api": "https://www.oakley.com/no-no/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.NORWAY],
        },
        {
            "api": "https://www.oakley.com/nl-nl/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.NETHERLANDS],
        },
        {
            "api": "https://www.oakley.com/fr-lu/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.LUXEMBOURG],
        },
        {
            "api": "https://www.oakley.com/it-it/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.ITALY],
        },
        {
            "api": "https://www.oakley.com/en-ie/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.IRELAND],
        },
        {
            "api": "https://www.oakley.com/de-de/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.GERMANY],
        },
        {
            "api": "https://www.oakley.com/fr-fr/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.FRANCE],
        },
        {
            "api": "https://www.oakley.com/en-dk/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.DENMARK],
        },
        {
            "api": "https://www.oakley.com/fr-be/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.BELGIUM],
        },
        {
            "api": "https://www.oakley.com/de-at/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.AUSTRIA],
        },
        {
            "api": "https://www.oakley.com/en-us/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.USA],
        },
        {
            "api": "https://www.oakley.com/es-mx/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.MEXICO],
        },
        {
            "api": "https://www.oakley.com/en-ca/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.CANADA],
        },
        {
            "api": "https://www.oakley.com/pt-br/store-finder/stores?lat={}&lng={}&q=&oakleyStore=true&_oakleyStore=on&oakleyVault=true&_oakleyVault=on&oakleyDealer=true&_oakleyDealer=on&eyewear=true&_eyewear=on&apparel=true&_apparel=on&footwear=true&_footwear=on&goggles=true&_goggles=on&watches=true&_watches=on&custom=true&_custom=on&perscription=true&_perscription=on&accessories=true&_accessories=on&accessoriesLenses=true&_accessoriesLenses=on&electronics=true&_electronics=on&other=true&_other=on",
            "countries": [SearchableCountries.BRAZIL],
        },
    ]
    for ap in apis:
        search = DynamicGeoSearch(
            country_codes=ap.get("countries"), expected_search_radius_miles=50
        )

        for lat, lng in search:
            api = str(ap.get("api")).format(lat, lng)
            r = session.get(api, headers=headers)
            js = r.json()["stores"]

            for j in js:
                a = j.get("addressMap") or {}
                street_address = a.get("streetAddress")
                city = a.get("addressLocality")
                state = a.get("addressRegion")
                postal = a.get("postalCode")
                country_code = a.get("addressCountry")
                store_number = j.get("id")
                location_name = j.get("name")
                slug = j.get("url")
                page_url = f"https://www.oakley.com{slug}"
                phone = j.get("phone")
                latitude = j.get("lat")
                longitude = j.get("lng")
                hours = j.get("hoursMap") or {}
                hours_of_operation = ";".join(hours.values())

                row = SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    latitude=latitude,
                    longitude=longitude,
                    phone=phone,
                    store_number=store_number,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.oakley.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
