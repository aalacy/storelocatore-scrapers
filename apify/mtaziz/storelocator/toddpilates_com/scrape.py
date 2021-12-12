from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from lxml import html
import json


logger = SgLogSetup().get_logger("toddpilates_com")
locator_domain_url = "https://www.toddpilates.com"

MISSING = SgRecord.MISSING
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}


def get_hoo(data_r_yelp_hoo):
    hours_xpath = '//table[contains(@class, "hours")]/tbody/tr'
    hours_tr_obj = data_r_yelp_hoo.xpath(hours_xpath)
    hoo_weekday_list = []
    hoo_time_list = []
    for tr in hours_tr_obj:
        hoo_weekday = tr.xpath("./th/p/text()")
        hoo_weekday_list.append(hoo_weekday)
        hoo_time = tr.xpath("./td/ul/li/p/text()")
        hoo_time_list.append(hoo_time)

    hoo_weekday_clean1 = [hwl for hwl in hoo_weekday_list if hwl]
    hoo_weekday_clean2 = ["".join(hwl) for hwl in hoo_weekday_clean1]
    logger.info(f"Weekday: {hoo_weekday_clean2}\n")

    hoo_time_clean1 = [htl for htl in hoo_time_list if htl]
    hoo_time_clean2 = [", ".join(htl) for htl in hoo_time_clean1 if htl]
    logger.info(f"Opening Hours: {hoo_time_clean2}\n")

    hoo_dict = dict(zip(hoo_weekday_clean2, hoo_time_clean2))
    logger.info(f"HOO Dict: {hoo_dict}\n")
    hoo_data = []
    for key, value in hoo_dict.items():
        if key and value:
            hood = f"{key} {value}"
            hoo_data.append(hood)
    hoo_data = "; ".join(hoo_data)
    logger.info(f"Hours of operation: {hoo_data}\n")
    if hoo_data:
        return hoo_data
    else:
        return MISSING


def get_lat_lng(data_r_yelp_lat_lng):
    lat_lng_xpath = '//a[contains(@href, "/map/toddpilates")]/div/img/@src'
    lat_lng_data = data_r_yelp_lat_lng.xpath(lat_lng_xpath)
    lat_lng_raw = "".join(lat_lng_data).split("&signature")[0].split(".png")[-1]
    logger.info(f"Latitude and Longitude Raw Data: {lat_lng_raw}")
    lat = lat_lng_raw.split("%2C")[0].replace("%7C", "")
    latitude = lat if lat else MISSING
    logger.info(f"Latitude: {latitude}")
    lng = lat_lng_raw.split("%2C")[-1]
    longitude = lng if lng else MISSING
    logger.info(f"Longitude: {longitude}")
    return (latitude, longitude)


def fetch_records(http: SgRequests):
    base_url = "https://www.toddpilates.com"
    r = http.get("https://www.toddpilates.com/", headers=headers)
    data_stores = html.fromstring(r.text, "lxml")
    url_stores = data_stores.xpath(
        '//div[div[div[contains(., "LOCATIONS")]]]/nav/a/@href'
    )
    url_stores = [f"{base_url}{i}" for i in url_stores]
    for num_store, url_store in enumerate(url_stores):
        locator_domain = locator_domain_url
        logger.info(f"Pulling the data from: {num_store} : {url_store} ")
        r_loc = http.get(url_store, headers=headers)
        data_r_loc = html.fromstring(r_loc.text, "lxml")
        if "https://www.toddpilates.com/se-austin" not in url_store:
            url_yelp = data_r_loc.xpath('//a[contains(@href, "yelp.com")]/@href')
            url_yelp = "".join(url_yelp)

            # Page URL
            page_url = url_yelp
            logger.info(f"Page URL: {page_url} ")

            # Get the data From Yelp as the data is not available on the site
            r_yelp = http.get(url_yelp, headers=headers)
            data_r_yelp = html.fromstring(r_yelp.text, "lxml")
            json_data_r_yelp = data_r_yelp.xpath(
                '//script[contains(@type, "application/ld+json") and contains(text(), "LocalBusiness")]/text()'
            )
            json_data_r_yelp = "".join(json_data_r_yelp)
            data = json.loads(json_data_r_yelp)
            location_name = data["name"].replace("&amp;", "&")
            logger.info(f"Location Name: {location_name}")

            # Get address
            add = data["address"]
            logger.info(f"Address: {add}")

            street_address = add["streetAddress"].replace("\n", ",")
            logger.info(f"Street Address: {street_address}")
            street_address = street_address if street_address else MISSING

            city = add["addressLocality"]
            logger.info(f"City: {city}")
            city = city if city else MISSING

            state = add["addressRegion"]
            logger.info(f"Location Name: {state}")
            state = state if state else MISSING

            zipcode = add["postalCode"]
            logger.info(f"Zip: {zipcode}")
            zipcode = zipcode if zipcode else MISSING

            country_code = add["addressCountry"]
            country_code = country_code if country_code else MISSING
            logger.info(f"Country Code: {country_code}")

            store_number = MISSING
            logger.info(f"Store Number: {store_number}")

            phone = data["telephone"]
            logger.info(f"Telephone: {phone}")
            phone = phone if phone else MISSING

            location_type = MISSING

            latlng = get_lat_lng(data_r_yelp)
            latitude = latlng[0]
            logger.info(f"Latitude: {latitude}")
            longitude = latlng[1]
            logger.info(f"Longitude: {longitude}")

            hours_of_operation = get_hoo(data_r_yelp)
            logger.info(f"HOO: {hours_of_operation}")

            # Raw Address
            raw_address = ""
            ra_xpath = '//div[p[a[contains(text(), "Get Directions")]]]/p/text()'
            ra_yelp = data_r_yelp.xpath(ra_xpath)
            ra_yelp = "".join(ra_yelp)
            if ra_yelp:
                raw_address = ra_yelp
            else:
                raw_address = MISSING
            logger.info(f" Raw Address from Yelp: {raw_address}")

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        else:
            # Get the data from another store which has different domain
            data_se_austin = data_r_loc
            location_name = data_se_austin.xpath(
                '//meta[@property="og:description"]/@content'
            )[0]
            location_name = location_name.replace(
                "The most affordable and fun cardio, strength and functional classes in Southeast Austin at the",
                "",
            )
            location_name = location_name.replace(
                "! 9110 Bluff Springs Rd., Austin, TX 78744.", ""
            ).strip()
            logger.info(f"Location Name: {location_name}")
            url_austin_pickle_ranch = data_se_austin.xpath(
                '//h1[@class="h1heading mainheading h1tablet plheading pickle"]/a/@href'
            )
            url_austin_pickle_ranch = "".join(url_austin_pickle_ranch)
            logger.info(f"Page URL: {url_austin_pickle_ranch}")

            # Page URL
            page_url = url_austin_pickle_ranch

            # Get Address
            r_austin_pickle_ranch = http.get(url_austin_pickle_ranch, headers=headers)
            data_austin_pickle_ranch = html.fromstring(
                r_austin_pickle_ranch.text, "lxml"
            )
            address = data_austin_pickle_ranch.xpath(
                '//address[@class="footer-address"]/text()'
            )
            street_address = address[0]
            logger.info(f"Street Address: {street_address}")

            city_state_zip = " ".join(address[-1].split())
            city = city_state_zip.split(",")[0]
            city = city if city else MISSING
            logger.info(f"City: {city}")

            state = city_state_zip.split(",")[-1].strip().split(" ")[0]
            state = state if state else MISSING
            logger.info(f"State: {state}")

            zipcode = city_state_zip.split(",")[-1].strip().split(" ")[-1]
            zipcode = zipcode if zipcode else MISSING
            logger.info(f"Zip Code: {zipcode}")

            country_code = "US"
            store_number = MISSING
            phone = "<INACCESSIBLE>"

            # Get location type
            location_type = ""
            loc_type = data_se_austin.xpath('//h1[@class="summer2021"]/text()')
            loc_type = "".join(loc_type)
            if "OPENING" in loc_type:
                location_type = "Coming Soon"
            else:
                location_type = MISSING
            logger.info(f"Location Type: {location_type}")

            # Get Latitude and longitude
            latlng = data_se_austin.xpath(
                '//div[contains(@class, "map-section w-hidden-main w-hidden-medium")]/div/div/@data-widget-latlng'
            )
            latlng = "".join(latlng).split(",")
            latitude = latlng[0] or MISSING
            logger.info(f"Latitude: {latitude}")
            longitude = latlng[1] or MISSING
            logger.info(f"Longitude: {longitude}")

            # HOO not found on the source page
            hours_of_operation = MISSING
            logger.info(f"Hours of operation: {hours_of_operation}")

            # Raw Address from source site
            raw_address = ""
            ra = address
            ra = ",".join(ra)
            ra = ra.split()
            ra = " ".join(ra)
            if ra:
                raw_address = ra
            else:
                raw_address = MISSING

            logger.info(f"Raw Address: {raw_address}")

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
