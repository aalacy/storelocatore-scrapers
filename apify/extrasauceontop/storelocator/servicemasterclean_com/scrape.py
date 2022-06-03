from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_8(),
        expected_search_radius_miles=100,
    )
    session = SgRequests()
    url = "https://www.servicemasterclean.com/locations/?CallAjax=GetLocations"
    for search_code in search:
        params = {
            "zipcode": search_code,
            "distance": "5000",
            "tab": "ZipSearch",
            "templates": {
                "Item": '&lt;li data-servicetype="[{ServiceTypeIDs}]" data-serviceid="[{ServiceIDs}]"&gt;\t&lt;h2&gt;{FranchiseLocationName}&lt;/h2&gt;\t&lt;div class="info flex"&gt;\t\t&lt;if field="GMBLink"&gt;\t\t\t&lt;span class="rating-{FN0:GMBReviewRatingScoreOutOfFive}"&gt;\t\t\t\t{FN1:GMBReviewRatingScoreOutOfFive}\t\t\t\t&lt;svg data-use="star.36" class="rate1"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate2"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate3"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate4"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate5"&gt;&lt;/svg&gt;\t\t\t&lt;/span&gt;\t\t\t&lt;a href="{http:GMBLink}" target="_blank"&gt;Visit Google My Business Page&lt;/a&gt;\t\t&lt;/if&gt;\t\t&lt;if field="YelpLink"&gt;\t\t\t&lt;span class="rating-{FN0:YelpReviewRatingScoreOutOfFive}"&gt;\t\t\t\t{FN1:YelpReviewRatingScoreOutOfFive}\t\t\t\t&lt;svg data-use="star.36" class="rate1"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate2"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate3"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate4"&gt;&lt;/svg&gt;\t\t\t\t&lt;svg data-use="star.36" class="rate5"&gt;&lt;/svg&gt;\t\t\t&lt;/span&gt;\t\t\t&lt;a href="{http:YelpLink}" target="_blank"&gt;Visit Yelp Page&lt;/a&gt;\t\t&lt;/if&gt;\t\t&lt;a class="flex" href="tel:{Phone}"&gt;\t\t\t&lt;svg data-use="phone.36"&gt;&lt;/svg&gt; {F:P:Phone}\t\t&lt;/a&gt;\t\t&lt;if field="Path"&gt;\t\t\t&lt;a href="{Path}" class="text-btn" rel="nofollow noopener"&gt;Website&lt;/a&gt;\t\t&lt;/if&gt;\t&lt;/div&gt;\t&lt;div class="type flex"&gt;\t\t&lt;strong&gt;Services:&lt;/strong&gt;\t\t&lt;ul&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2638"&gt;\t\t\t\t&lt;li&gt;Commercial&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2658"&gt;\t\t\t\t&lt;li&gt;Residential&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t\t&lt;if field="{ServiceIDs}" contains="2634"&gt;\t\t\t\t&lt;li&gt;Janitorial&lt;/li&gt;\t\t\t&lt;/if&gt;\t\t&lt;/ul&gt;\t&lt;/div&gt;&lt;/li&gt;'
            },
        }
        response = session.post(url, json=params).json()

        try:
            if response[0]["Message"] == "Zip Code Not Found":
                continue

        except Exception:
            pass
        for location in response:
            locator_domain = "www.servicemasterclean.com"
            page_url = "https://www.servicemasterclean.com" + location["Path"]
            location_name = location["BusinessName"]
            latitude = location["Latitude"]
            longitude = location["Longitude"]
            city = location["City"]
            state = location["State"]
            store_number = location["FranchiseLocationID"]
            address = location["Address1"]
            zipp = location["ZipCode"]
            phone = location["Phone"]
            location_type = "<MISSING>"
            hours = "<LATER>"
            country_code = location["Country"]
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
        duplicate_streak_failure_factor=-1,
    )
    pipeline.run()


scrape()
