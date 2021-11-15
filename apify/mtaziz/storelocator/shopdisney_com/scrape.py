from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json


logger = SgLogSetup().get_logger("shopdisney_com")
MISSING = SgRecord.MISSING
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

# This API ENDPOINT URL returns the data for the US anc CA
US_API_ENDPOINT_URL = "https://locations.shopdisney.com/rest/locatorsearch?lang=en_US"
US_PAYLOAD = {
    "request": {
        "appkey": "4E6D88C8-024F-11E6-8672-4E1F407E493E",
        "formdata": {
            "geoip": False,
            "dynamicSearch": True,
            "noZoomOnPan": False,
            "dataview": "store_default",
            "limit": 200,
            "geolocs": {
                "geoloc": [
                    {
                        "addressline": "newyork",
                        "country": "US",
                        "latitude": 40.7127753,
                        "longitude": -74.0059728,
                        "state": "NY",
                        "province": "",
                        "city": "New York",
                        "address1": "",
                        "postalcode": "",
                    }
                ]
            },
            "searchradius": "5000",
            "where": {"and": {"storetype": {"eq": ""}}},
            "false": "0",
            "true": "1",
        },
    }
}

# This API ENDPOINT URL returns the data for European countries
# that include Spain, France, Great Britain, Ireland, Italy and Portugal
UK_API_ENDPOINT_URL = "https://locations.shopdisney.co.uk/rest/locatorsearch?lang=en_US"
UK_PAYLOAD = {
    "request": {
        "appkey": "9564CFF2-CE09-11DD-A3E6-0DBA3B999D57",
        "formdata": {
            "geoip": False,
            "dynamicSearch": True,
            "noZoomOnPan": False,
            "dataview": "store_default",
            "limit": 200,
            "geolocs": {
                "geoloc": [
                    {
                        "addressline": "london",
                        "country": "UK",
                        "latitude": 51.5073509,
                        "longitude": -0.1277583,
                        "state": "",
                        "province": "Greater London",
                        "city": "London",
                        "address1": "",
                        "postalcode": "",
                    }
                ]
            },
            "searchradius": "5000",
            "where": {
                "clientkey": {"distinctfrom": 12345},
                "or": {
                    "disney_store": {"eq": ""},
                    "disney_outlet": {"eq": ""},
                    "disney_baby": {"eq": ""},
                    "disney_closing": {"eq": ""},
                },
            },
            "false": "0",
            "true": "1",
        },
    }
}


def fetch_records(http: SgRequests):
    us_r = http.post(US_API_ENDPOINT_URL, headers=headers, data=json.dumps(US_PAYLOAD))
    us_json_response_collection = json.loads(us_r.content)["response"]["collection"]
    logger.info(f"Pulling the data from: {US_API_ENDPOINT_URL}")

    uk_r = http.post(UK_API_ENDPOINT_URL, headers=headers, data=json.dumps(UK_PAYLOAD))
    uk_json_response_collection = json.loads(uk_r.content)["response"]["collection"]
    logger.info(f"Pulling the data from: {UK_API_ENDPOINT_URL}")

    us_json_response_collection.extend(uk_json_response_collection)
    for idx, _ in enumerate(us_json_response_collection[0:]):
        page_url = MISSING
        if "localpage_url" in _:
            page_url = _["localpage_url"]
        else:
            page_url = MISSING

        location_name = _["name"]
        if "outlet" in location_name.lower():
            location_name = "Disney Outlet"
        else:
            location_name = "Disney Store"
        logger.info(f"[{idx}]: {location_name}")
        street_address = _["address1"]
        try:
            street_address = street_address + " " + _["address2"]
        except:
            pass
        street_address = street_address.strip()

        state = _["state"] or MISSING
        city = _["city"] or MISSING
        zip_postal = _["postalcode"] or MISSING
        country_code = _["country"] or MISSING
        if country_code == "UK":
            country_code = "GB"

        store_number = _["clientkey"]

        # Build page URLs for European stores based on it's city, store number
        # and UK store locator domain
        city_for_page_url = ""
        if "US" not in country_code:
            if "ORIO AL SERIO - BERGAMO" in city:
                city = "BERGAMO".lower()
                if MISSING not in store_number:
                    page_url = (
                        "https://stores.shopdisney.co.uk/" + city + "/" + store_number
                    )
            else:
                city_for_page_url = city.replace(" ", "-").lower()
                if MISSING not in store_number:
                    page_url = (
                        "https://stores.shopdisney.co.uk/"
                        + city_for_page_url
                        + "/"
                        + store_number
                    )

        phone = _["phone"] or MISSING

        location_type = ""
        if "storetype" in _:
            location_type = _["storetype"]
        else:
            location_type = MISSING

        lat = _["latitude"]
        latitude = lat if lat else MISSING
        lng = _["longitude"]
        longitude = lng if lng else MISSING
        locator_domain = "shopdisney.com"

        # Hours of Operation
        hours_of_operation = ""
        mon_op = str(_["mon_op"] or "")
        tue_op = str(_["tue_op"] or "")
        wed_op = str(_["wed_op"] or "")
        thu_op = str(_["thu_op"] or "")
        fri_op = str(_["fri_op"] or "")
        sat_op = str(_["sat_op"] or "")
        sun_op = str(_["sun_op"] or "")
        mon_cl = str(_["mon_cl"] or "")
        tue_cl = str(_["tue_cl"] or "")
        wed_cl = str(_["wed_cl"] or "")
        thu_cl = str(_["thu_cl"] or "")
        fri_cl = str(_["fri_cl"] or "")
        sat_cl = str(_["sat_cl"] or "")
        sun_cl = str(_["sun_cl"] or "")

        sun = "Sun: " + sun_op + " - " + sun_cl
        mon = "Mon: " + mon_op + " - " + mon_cl
        tue = "Tue: " + tue_op + " - " + tue_cl
        wed = "Wed: " + wed_op + " - " + wed_cl
        thu = "Thu: " + thu_op + " - " + thu_cl
        fri = "Fri: " + fri_op + " - " + fri_cl
        sat = "Sat: " + sat_op + " - " + sat_cl
        hours = [sun, mon, tue, wed, thu, fri, sat]
        hours_of_operation = "; ".join(hours)
        raw_address = MISSING
        yield SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Scrape started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
