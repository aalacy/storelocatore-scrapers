# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape import simple_scraper_pipeline as sp
from sgzip.static import static_coordinate_list
from sgzip.dynamic import SearchableCountries

website = "citygear.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.hibbett.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hibbett.com/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_data():
    # Your scraper here
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)[
        :50
    ]
    url_list = []
    for lat, lng in coords:
        log.info(f"Pulling stores for {lat,lng}")
        url = (
            "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/"
            "default/Stores-GetNearestStores?latitude={}&"
            "longitude={}&countryCode=US&distanceUnit=mi&maxdistance=2500000"
        )
        stores_req = session.get(
            url.format(lat, lng),
            headers=headers,
        )
        stores = json.loads(stores_req.text.strip())["stores"]
        for store in stores.keys():
            locator_domain = website
            location_name = stores[store]["name"]
            if location_name != "Hibbett Sports":
                continue
            street_address = stores[store]["address1"]
            if len(stores[store]["address2"]) > 0:
                street_address = street_address + ", " + stores[store]["address2"]
            city = stores[store]["city"]
            state = stores[store]["stateCode"]
            zipp = stores[store]["postalCode"]
            country_code = stores[store]["countryCode"]
            page_url = (
                "https://www.hibbett.com/storedetails/"
                + state
                + "/"
                + city
                + "/"
                + stores[store]["id"]
            )
            if page_url in url_list:
                continue

            url_list.append(page_url)
            phone = stores[store]["phone"]
            store_number = stores[store]["id"]

            location_type = "<MISSING>"
            if stores[store]["isOpeningSoon"] is True:
                location_type = "Opening Soon"

            if stores[store]["temporarilyClosed"] is True:
                location_type = "Temporarily Closed"

            latitude = stores[store]["latitude"]
            longitude = stores[store]["longitude"]
            hours_of_operation = stores[store]["storeHours"].replace("|", " ").strip()

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip": zipp,
                "country_code": country_code,
                "store_number": store_number,
                "phone": phone,
                "location_type": location_type,
                "latitude": latitude,
                "longitude": longitude,
                "hours": hours_of_operation,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"], is_required=False),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
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
