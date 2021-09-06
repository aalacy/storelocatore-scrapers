from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
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


DOMAIN = "towneplacesuites.marriott.com"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"
logger = SgLogSetup().get_logger("towneplacesuites_marriott_com")

headers_api = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


# Marriott Hotels has total 30 brands.
# Note: Marriott Hotels ( MC ) contains MC and MV (Marriott Vacation Club) brands as well
# This contributes total 23 brands out of 30 brands
# There are 22 API_ENDPOINT URLs but it will return the data for 23 brands
# The rest of the 7 brands will be scraped using manual scraping method
# At the time of scraping total 23 brands contritubes store count 7642

url_api_endpoints_23_brands = {
    "https://ac-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_AR_en-US.json",
    "https://aloft-hotels.marriott.com/locations/": "https://pacsys.marriott.com/data/marriott_properties_AL_en-US.json",
    "https://autograph-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_AK_en-US.json",
    "https://courtyard.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_CY_en-US.json",
    "https://delta-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_DE_en-US.json",
    "https://design-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_DS_en-US.json",
    "https://element-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_EL_en-US.json",
    "https://fairfield.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_FI_en-US.json",
    "https://four-points.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_FP_en-US.json",
    "https://jw-marriott.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_JW_en-US.json",
    "https://marriott-hotels.marriott.com/locations/": "https://pacsys.marriott.com/data/marriott_properties_MC_en-US.json",
    "https://moxy-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_OX_en-US.json",
    "https://residence-inn.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_RI_en-US.json",
    "https://sheraton.marriott.com": "https://pacsys.marriott.com/data/marriott_properties_SI_en-US.json",
    "https://springhillsuites.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_SH_en-US.json",
    "https://le-meridien.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_MD_en-US.json",
    "https://the-luxury-collection.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_LC_en-US.json",
    "https://towneplacesuites.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_TS_en-US.json",
    "https://tribute-portfolio.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_TX_en-US.json",
    "https://w-hotels.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_WH_en-US.json",
    "https://westin.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_WI_en-US.json",
    "https://st-regis.marriott.com/": "https://pacsys.marriott.com/data/marriott_properties_XR_en-US.json",
}


def fetch_data_for_23_child_brands_from_api_endpoints():
    with SgRequests() as session:
        for k, v in url_api_endpoints_23_brands.items():
            url = v
            x = 0
            while True:
                x = x + 1
                try:
                    response = session.get(url, headers=headers_api, timeout=500)
                    break
                except Exception as e:
                    logger.info("")
                    logger.info(e)
                    if x == 10:
                        raise Exception(
                            "Make sure this ran with a Proxy, will fail without one"
                        )
                    continue

            logger.info("JSON data being loaded...")
            response_text = response.text
            store_list = json.loads(response_text)
            data_8 = store_list["regions"]
            for i in data_8:
                for j in i["region_countries"]:
                    for k in j["country_states"]:
                        for h in k["state_cities"]:
                            for g in h["city_properties"]:
                                locator_domain = DOMAIN
                                key = g["marsha_code"]
                                if key:
                                    page_url = f"{'https://www.marriott.com/hotels/travel/'}{str(key)}"
                                else:
                                    page_url = SgRecord.MISSING
                                logger.info(f"[Page URL: {page_url} ]")

                                # Location Name
                                location_name = g["name"]
                                location_name = (
                                    location_name if location_name else SgRecord.MISSING
                                )

                                # Street Address
                                street_address = g["address"]
                                street_address = (
                                    street_address
                                    if street_address
                                    else SgRecord.MISSING
                                )

                                # City
                                city = g["city"]
                                city = city if city else SgRecord.MISSING

                                # State
                                state = g["state_name"]
                                state = state if state else SgRecord.MISSING

                                # Zip Code
                                zip_postal = g["postal_code"]
                                zip_postal = (
                                    zip_postal if zip_postal else SgRecord.MISSING
                                )

                                # Country Code
                                country_code = g["country_name"]
                                country_code = (
                                    country_code if country_code else SgRecord.MISSING
                                )

                                # Store Number
                                store_number = SgRecord.MISSING

                                # Phone
                                phone = g["phone"]
                                phone = phone if phone else SgRecord.MISSING

                                # Location Type
                                location_type = g["brand_code"]
                                if location_type:
                                    location_type = location_type + " " + "Hotels"
                                else:
                                    location_type = SgRecord.MISSING
                                # Latitude
                                latitude = g["latitude"]
                                latitude = latitude if latitude else SgRecord.MISSING

                                # Longitude
                                longitude = g["longitude"]
                                longitude = longitude if longitude else longitude

                                # Number of Operations

                                hours_of_operation = ""
                                hours_of_operation = (
                                    hours_of_operation
                                    if hours_of_operation
                                    else SgRecord.MISSING
                                )

                                # Raw Address
                                raw_address = ""
                                raw_address = (
                                    raw_address if raw_address else SgRecord.MISSING
                                )

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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results_23_brands = fetch_data_for_23_child_brands_from_api_endpoints()
        for rec in results_23_brands:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
