from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4
from sglogging import sglog


def get_data():
    log = sglog.SgLogSetup().get_logger(logger_name="7eleven")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_4()
    )

    session = SgRequests()
    headers = {
        "Authority": "www.7-eleven.com",
        "Method": "GET",
        "Path": "/locator",
        "Scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36",
    }

    response = session.get("https://www.7-eleven.com/locator", headers=headers).text
    auth_token = response.split('access_token":')[1].split('"')[1]

    headers = {
        "Authorization": "Bearer " + auth_token,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36",
        "Host": "api.7-eleven.com",
        "Origin": "https://www.7-eleven.com",
        "Referer": "https://www.7-eleven.com/",
        "Accept": "application/json, text/plain, */*",
    }

    lats_lngs = []
    for search_lat, search_lon in search:
        url = f"https://api.7-eleven.com/v4/stores?lat={search_lat}&lon={search_lon}&radius=10000&curr_lat={search_lat}&curr_lon={search_lon}&limit=500&features="

        x = 0
        while True:
            x = x + 1
            if x == 10:
                log.info(url)
                log.info(session.get(url, headers=headers).text)
                raise Exception
            try:
                data = session.get(url, headers=headers).json()
                break
            except Exception:
                continue

        locations = data["results"]

        for location in locations:
            locator_domain = "7-eleven.com"
            page_url = url
            location_name = location["name"]
            address = location["address"]
            city = location["city"]
            state = location["state"]
            country_code = location["country"]
            zipp = location["zip"]

            if zipp[0] == 0:
                zipp = "0" + str(zipp)
            elif len(str(zipp)) == 4:
                zipp = "0" + str(zipp)
            store_number = location["id"]
            phone = location["phone"]
            if len(phone) < 5:
                phone = "<MISSING>"
            location_type = "<MISSING>"
            latitude = location["lat"]
            longitude = location["lon"]

            hours = ""
            if location["open_time"] == "24h":
                hours = location["open_time"]
            else:
                try:
                    for item in location["hours"]["operating"]:
                        hours = hours + item["key"] + " "
                        hours = hours + item["detail"] + ", "

                    hours = hours[:-2]
                except Exception:
                    hours = "<MISSING>"

            search.found_location_at(latitude, longitude)
            if [latitude, longitude] in lats_lngs:
                continue

            lats_lngs.append([latitude, longitude])

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
        page_url=sp.MappingField(mapping=["page_url"]),
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
