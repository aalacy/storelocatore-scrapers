from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8


def get_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        granularity=Grain_8(),
    )
    session = SgRequests()
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    for search_code in search:
        url = (
            "https://storelocations.ae.com/search.html?q="
            + str(search_code)
            + "&qp="
            + str(search_code)
            + "&l=en"
        )

        x = 0
        while True:
            x = x + 1
            if x == 10:
                raise Exception
            try:
                response = session.get(url, headers=headers).json()
                break
            except Exception:
                session.set_proxy_url(
                    "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"
                )

        for location in response["response"]["entities"]:
            locator_domain = "ae.com"
            page_url = location["profile"]["c_americanEaglePages"]
            location_name = location["profile"]["address"]["extraDescription"]
            try:
                latitude = location["profile"]["geocodedCoordinate"]["lat"]
                longitude = location["profile"]["geocodedCoordinate"]["long"]
            except Exception:
                latitude = location["profile"]["yextDisplayCoordinate"]["lat"]
                longitude = location["profile"]["yextDisplayCoordinate"]["long"]
            city = location["profile"]["address"]["city"]
            store_number = location["distance"]["id"]
            address = (
                (
                    str(location["profile"]["address"]["line1"])
                    + " "
                    + str(location["profile"]["address"]["line2"])
                    + " "
                    + str(location["profile"]["address"]["line3"])
                )
                .replace("  ", " ")
                .replace("None", "")
                .strip()
            )
            state = location["profile"]["address"]["region"]
            zipp = location["profile"]["address"]["postalCode"]
            phone = location["profile"]["mainPhone"]["number"].replace("+", "")

            try:
                location_type = ""
                for type in location["profile"]["brands"]:
                    location_type = location_type + type + ","

                location_type = location_type[:-1]

            except Exception:
                location_type = "<MISSING>"

            hours = "<LATER>"
            country_code = location["profile"]["address"]["countryCode"]
            search.found_location_at(latitude, longitude)
            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
                "country_code": country_code,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
