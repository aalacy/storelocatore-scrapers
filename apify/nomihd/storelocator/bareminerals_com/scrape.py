# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bareminerals.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://hosted.where2getit.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_us_data():
    # Your scraper here
    search_url = "https://stores.bareminerals.com/"
    states_req = session.get(search_url, headers=headers)
    states_sel = lxml.html.fromstring(states_req.text)
    states = states_sel.xpath('//div[@class="itemlist"]/a/@href')
    for state_url in states:
        cities_req = session.get(state_url, headers=headers)
        cities_sel = lxml.html.fromstring(cities_req.text)
        cities = cities_sel.xpath('//div[@class="itemlist"]/a/@href')
        for city_url in cities:
            stores_req = session.get(city_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//li/a[contains(text(),"View Store Details")]/@href'
            )
            for store_url in stores:
                page_url = store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                store_json = None
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                for js in json_list:
                    if '"@type":"HealthAndBeautyBusiness"' in js:
                        store_json = json.loads(
                            js.replace(
                                "//if applied, use the tmpl_var to retrieve the database value",
                                "",
                            )
                            .strip()
                            .replace('//"', '"')
                            .strip()
                            .split('"menu"')[0]
                            .strip()
                            + "}"
                        )

                locator_domain = website
                location_name = store_json["name"]

                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]

                country_code = store_json["address"]["addressCountry"]

                store_number = "<MISSING>"
                phone = store_json["telephone"]
                location_type = "<MISSING>"
                hours = store_json["openingHoursSpecification"]
                hours_of_operation = ""
                for hour in hours:
                    day = hour["dayOfWeek"][0]
                    time = hour["opens"] + "-" + hour["closes"]
                    hours_of_operation = hours_of_operation + day + ":" + time + " "

                hours_of_operation = hours_of_operation.strip()
                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def fetch_records_for(tup):
    coords, CurrentCountry, countriesRemaining = tup
    lat = coords[0]
    lng = coords[1]
    log.info(
        f"pulling records for Country-{CurrentCountry} Country#:{countriesRemaining},\n coordinates: {lat,lng}"
    )
    search_url = "https://hosted.where2getit.com/bareminerals/rest/locatorsearch"
    data = {
        "request": {
            "appkey": "36800888-F9C9-11E9-9309-C680DEB8F1E5",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "google_autocomplete": "true",
                "limit": 250,
                "order": "rank::numeric, _distance",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "",
                            "country": CurrentCountry,
                            "latitude": lat,
                            "longitude": lng,
                            "state": "",
                            "province": "",
                            "city": "",
                            "address1": "",
                            "postalcode": "",
                        }
                    ]
                },
                "searchradius": "10|25|50|100|250",
                "radiusuom": "mile",
                "where": {
                    "mono_solution_subscription": {"eq": ""},
                    "or": {"storetype": {"eq": "BE_BOUTIQUE"}},
                },
                "false": "0",
            },
        }
    }

    stores = []
    stores_req = session.post(search_url, headers=headers, data=json.dumps(data))
    try:
        stores = json.loads(stores_req.text)["response"]["collection"]
    except:
        pass

    return stores, CurrentCountry


def process_record(raw_results_from_one_coordinate):
    stores, current_country = raw_results_from_one_coordinate
    for store in stores:
        page_url = "https://www.bareminerals.com/find-a-store/"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store.get("city", "<MISSING>")
        state = store.get("state", "<MISSING>")
        zip = store.get("postalcode", "<MISSING>")
        country_code = store["country"]
        if country_code is None or country_code == "":
            country_code = current_country

        store_number = "<MISSING>"
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        hours_list = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for key in store.keys():
            if key in days:
                day = key
                time = store[day]
                if time is not None:
                    hours_list.append(day + ": " + time)

        if len(hours_list) <= 0:
            try:
                for key in store.keys():
                    if key == "monopen":
                        if store["monopen"]:
                            day = "Monday:"
                            time = store["monopen"] + " - " + store["monclose"]
                            hours_list.append(day + time)
                    if key == "tueopen":
                        if store["tueopen"]:
                            day = "Tuesday:"
                            time = store["tueopen"] + " - " + store["tueclose"]
                            hours_list.append(day + time)
                    if key == "wedopen":
                        if store["wedopen"]:
                            day = "Wednesday:"
                            time = store["wedopen"] + " - " + store["wedclose"]
                            hours_list.append(day + time)
                    if key == "thuopen":
                        if store["thuopen"]:
                            day = "Thursday:"
                            time = store["thuopen"] + " - " + store["thuclose"]
                            hours_list.append(day + time)
                    if key == "friopen":
                        if store["friopen"]:
                            day = "Friday:"
                            time = store["friopen"] + " - " + store["friclose"]
                            hours_list.append(day + time)
                    if key == "satopen":
                        if store["satopen"]:
                            day = "Saturday:"
                            time = store["satopen"] + " - " + store["satclose"]
                            hours_list.append(day + time)
                    if key == "sunopen":
                        if store["sunopen"]:
                            day = "Sunday:"
                            time = store["sunopen"] + " - " + store["sunclose"]
                            hours_list.append(day + time)

            except:
                pass
        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["latitude"]
        longitude = store["longitude"]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        countries = ["US", "AT", "CA", "FR", "DE", "IE", "GB"]

        totalCountries = len(countries)
        currentCountryCount = 0
        for country in countries:
            if country != "US":
                try:
                    search = DynamicGeoSearch(
                        expected_search_radius_miles=5, country_codes=[country]
                    )
                    results = parallelize(
                        search_space=[
                            (
                                coord,
                                country,
                                str(f"{currentCountryCount}/{totalCountries}"),
                            )
                            for coord in search
                        ],
                        fetch_results_for_rec=fetch_records_for,
                        processing_function=process_record,
                    )
                    for rec in results:
                        writer.write_row(rec)
                        count = count + 1
                    currentCountryCount += 1
                except Exception as e:
                    log.error(f"{country}: not found\n{e}")
                    currentCountryCount += 1
                    pass
            else:
                results = fetch_us_data()
                for rec in results:
                    writer.write_row(rec)
                    count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
