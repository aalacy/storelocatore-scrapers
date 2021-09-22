from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("dollartree_com")

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

DOMAIN = "dollartree.com"
MISSING = SgRecord.MISSING
session = SgRequests().requests_retry_session(retries=10, backoff_factor=0.3)


# It is noted that when expected search radius miles is set to 100 miles along with granualrity ( Grain_8 ) -
# it returns 7915 records.
# It is also observed that with 100 miles radius, it returns 7915 records.
# Multiple times, it was tested with different settings and it max. returns 7915 records.


search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
    expected_search_radius_miles=200,
    max_search_results=1000,
    use_state=True,
    granularity=Grain_8(),
)


def fetch_data():
    # Your scraper here
    total = 0
    maxZ = search.items_remaining()
    location_url_state_city_with_hyphen_clientkey_part1_us = (
        "https://www.dollartree.com/locations/"
    )
    location_url_state_city_with_hyphen_clientkey_part1_ca = (
        "https://locations.dollartreecanada.com/"
    )
    start_url = (
        "https://hosted.where2getit.com/dollartree/rest/locatorsearch?lang=en_US"
    )

    for zipcode in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        body = '{"request":{"appkey":"134E9A7A-AB8F-11E3-80DE-744E58203F82","formdata":{"geoip":false,"dataview":"store_default","limit":1000,"order":"_DISTANCE","geolocs":{"geoloc":[{"addressline":"%s","country":"","latitude":"","longitude":""}]},"searchradius":"500","radiusuom":"","where":{"icon":{"eq":""},"ebt":{"eq":""},"freezers":{"eq":""},"crafters_square":{"eq":""},"snack_zone":{"eq":""},"distributioncenter":{"distinctfrom":"1"}},"false":"0"}}}'
        body_zipcode = body % zipcode
        api_end_point_url = f"{start_url}{body_zipcode}"
        logger.info(("Pulling zip Code %s... %s" % (zipcode, api_end_point_url)))
        response = session.post(
            start_url, data=body % zipcode, headers=headers, timeout=180
        )
        data = json.loads(response.text)

        if not data["response"].get("collection"):
            continue
        total += len(data["response"]["collection"])
        for poi in data["response"]["collection"]:
            search.found_location_at(
                poi["latitude"],
                poi["longitude"],
            )
            locator_domain = DOMAIN
            location_name = poi["name"]
            location_name = location_name if location_name else MISSING
            street_address = poi["address1"]
            street_address = street_address if street_address else MISSING

            # City
            city = poi["city"]

            # City name will be used to form the Page URL
            city_url = city.replace(" ", "-").lower()
            city = city if city else MISSING
            state = poi["state"]
            if not state:
                state = poi["province"]
            state_url = state.lower()
            state = state if state else MISSING
            zip_postal = poi["postalcode"]
            zip_postal = zip_postal if zip_postal else MISSING
            country_code = poi["country"]
            country_code = country_code if country_code else MISSING
            store_number = poi["clientkey"]

            # client key to be used to form the Page URL
            clientkey_url = store_number

            store_number = store_number if store_number else MISSING
            phone = poi["phone"]
            phone = phone if phone else MISSING
            location_type = MISSING
            location_type = location_type if location_type else MISSING
            latitude = poi["latitude"]
            latitude = latitude if latitude else MISSING
            longitude = poi["longitude"]
            longitude = longitude if longitude else MISSING
            hours_of_operation = poi["hours"]
            if poi["hours2"]:
                hours_of_operation += ", " + poi["hours2"]
            if not hours_of_operation:
                hours_of_operation = []
                for key, value in poi.items():
                    if "hours" in key:
                        if not value:
                            continue
                        hours_of_operation.append(value)
                hours_of_operation = ", ".join(hours_of_operation)
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING
            raw_address = poi["address1"]
            if poi.get("address2"):
                raw_address += " " + poi["address2"]
            if poi.get("address3"):
                raw_address += " " + poi["address3"]
            if country_code == "US":
                page_url = f"{location_url_state_city_with_hyphen_clientkey_part1_us}{state_url}/{city_url}/{clientkey_url}/"
            elif country_code == "CA":
                page_url = f"{location_url_state_city_with_hyphen_clientkey_part1_ca}{state_url}/{city_url}/{clientkey_url}/"
            else:
                page_url = MISSING

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(
            f"found: {len(data['response']['collection'])} | total: {total} | progress: {progress}"
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
