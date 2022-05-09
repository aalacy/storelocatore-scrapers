from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("hellyhansen_com")
DOMAIN = "hellyhansen.com"
MISSING = SgRecord.MISSING
MAX_WORKERS = 5
headers_ = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(50))
def get_response(url):
    with SgRequests(verify_ssl=False, timeout_config=400) as http:
        response = http.get(url, headers=headers_)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


API_ENDPOINT_URL_LIST = [
    "https://helly-hansen.locally.com/stores/conversion_data?has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat=29.232654996722218&map_center_lng=-89.62658124998006&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4&lang=en-us",
    "https://helly-hansen.locally.com/stores/conversion_data?has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat=47.823607476861554&map_center_lng=2.6187869531297565&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=France&zoom_level=9&lang=en-us&forced_coords=",
    "https://helly-hansen.locally.com/stores/conversion_data?has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat=47.38579850902305&map_center_lng=-70.4381377979114&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=9&lang=en-us",
]


def format_hour_min(raw_time):
    h_and_m = ""
    suno_h = ""
    suno_m = ""
    if len(raw_time) == 3:
        suno_h = raw_time[-3]
        suno_m = raw_time[-2:]
    if len(raw_time) == 4:
        suno_h = raw_time[:-2]
        suno_m = raw_time[-2:]
    h_and_m = suno_h + ":" + suno_m
    return h_and_m


def get_hour_min_for_a_day(suno, sunc):
    sun = ""
    if suno == 0 and sunc == 0:
        sun = "Closed"
    else:
        if not suno and not sunc:
            sun = ""
        else:
            sun = format_hour_min(str(suno)) + " - " + format_hour_min(str(sunc))
    return sun


def fetch_records_eu_based_on_france(latlng, sgw):
    items = []
    total = 0
    lat, lng = latlng
    conversion_data_base_url = (
        "https://helly-hansen.locally.com/stores/conversion_data?"
    )
    input_keys = f"has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat={str(lat)}&map_center_lng={str(lng)}&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=France&zoom_level=9&lang=en-us&forced_coords="
    api_endpoint_url = f"{conversion_data_base_url}{input_keys}"

    try:
        r = get_response(api_endpoint_url)
        js = json.loads(r.content)["markers"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for idx, _ in enumerate(js[0:]):
                hoo = ""
                suno = ""
                if "sun_time_open" in _:
                    suno = _["sun_time_open"]
                sunc = ""
                if "sun_time_close" in _:
                    sunc = _["sun_time_close"]

                mono = ""
                if "mon_time_open" in _:
                    mono = _["mon_time_open"]
                monc = ""
                if "mon_time_close" in _:
                    monc = _["mon_time_close"]

                tueo = ""
                if "tue_time_open" in _:
                    tueo = _["tue_time_open"]
                tuec = ""
                if "tue_time_close" in _:
                    tuec = _["tue_time_close"]

                wedo = ""
                if "wed_time_open" in _:
                    wedo = _["wed_time_open"]
                wedc = ""
                if "wed_time_close" in _:
                    wedc = _["wed_time_close"]

                thuo = ""
                if "thu_time_open" in _:
                    thuo = _["thu_time_open"]

                thuc = ""
                if "thu_time_close" in _:
                    thuc = _["thu_time_close"]

                frio = ""
                if "fri_time_open" in _:
                    frio = _["fri_time_open"]
                fric = ""
                if "fri_time_close" in _:
                    fric = _["fri_time_close"]

                sato = ""
                if "sat_time_open" in _:
                    sato = _["sat_time_open"]
                satc = ""
                if "sat_time_close" in _:
                    satc = _["sat_time_close"]

                sunoc = get_hour_min_for_a_day(suno, sunc)
                monoc = get_hour_min_for_a_day(mono, monc)
                tueoc = get_hour_min_for_a_day(tueo, tuec)
                wedoc = get_hour_min_for_a_day(wedo, wedc)
                thuoc = get_hour_min_for_a_day(thuo, thuc)
                frioc = get_hour_min_for_a_day(frio, fric)
                satoc = get_hour_min_for_a_day(sato, satc)
                date_open_close = list(
                    set([sunoc, monoc, tueoc, wedoc, thuoc, frioc, satoc])
                )

                if not date_open_close:
                    hoo = "<MISSING>"
                else:
                    hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                if "Sun: , Mon: , Tue: , Wed: , Thu: , Fri: , Sat:" in hoo:
                    hoo = MISSING
                item = SgRecord(
                    locator_domain="hellyhansen.com",
                    page_url="",
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    store_number=_["id"],
                    phone=_["phone"],
                    location_type=_["slug"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation=hoo,
                    raw_address="",
                )
                items.append(item.as_dict())

                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["markers"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> << {api_endpoint_url} >> "
        )


# LatLng of Chile actually does not work


def fetch_records_eu_based_on_chile(latlng, sgw):
    items = []
    total = 0
    lat, lng = latlng
    conversion_data_base_url = (
        "https://helly-hansen.locally.com/stores/conversion_data?"
    )
    input_keys = f"has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat={str(lat)}&map_center_lng={str(lng)}&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=9&lang=en-us&forced_coords="
    api_endpoint_url = f"{conversion_data_base_url}{input_keys}"

    try:
        r = get_response(api_endpoint_url)
        js = json.loads(r.content)["markers"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for idx, _ in enumerate(js[0:]):
                hoo = ""
                suno = ""
                if "sun_time_open" in _:
                    suno = _["sun_time_open"]
                sunc = ""
                if "sun_time_close" in _:
                    sunc = _["sun_time_close"]

                mono = ""
                if "mon_time_open" in _:
                    mono = _["mon_time_open"]
                monc = ""
                if "mon_time_close" in _:
                    monc = _["mon_time_close"]

                tueo = ""
                if "tue_time_open" in _:
                    tueo = _["tue_time_open"]
                tuec = ""
                if "tue_time_close" in _:
                    tuec = _["tue_time_close"]

                wedo = ""
                if "wed_time_open" in _:
                    wedo = _["wed_time_open"]
                wedc = ""
                if "wed_time_close" in _:
                    wedc = _["wed_time_close"]

                thuo = ""
                if "thu_time_open" in _:
                    thuo = _["thu_time_open"]

                thuc = ""
                if "thu_time_close" in _:
                    thuc = _["thu_time_close"]

                frio = ""
                if "fri_time_open" in _:
                    frio = _["fri_time_open"]
                fric = ""
                if "fri_time_close" in _:
                    fric = _["fri_time_close"]

                sato = ""
                if "sat_time_open" in _:
                    sato = _["sat_time_open"]
                satc = ""
                if "sat_time_close" in _:
                    satc = _["sat_time_close"]

                sunoc = get_hour_min_for_a_day(suno, sunc)
                monoc = get_hour_min_for_a_day(mono, monc)
                tueoc = get_hour_min_for_a_day(tueo, tuec)
                wedoc = get_hour_min_for_a_day(wedo, wedc)
                thuoc = get_hour_min_for_a_day(thuo, thuc)
                frioc = get_hour_min_for_a_day(frio, fric)
                satoc = get_hour_min_for_a_day(sato, satc)
                date_open_close = list(
                    set([sunoc, monoc, tueoc, wedoc, thuoc, frioc, satoc])
                )

                if not date_open_close:
                    hoo = "<MISSING>"
                else:
                    hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                if "Sun: , Mon: , Tue: , Wed: , Thu: , Fri: , Sat:" in hoo:
                    hoo = MISSING
                item = SgRecord(
                    locator_domain="hellyhansen.com",
                    page_url="",
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    store_number=_["id"],
                    phone=_["phone"],
                    location_type=_["slug"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation=hoo,
                    raw_address="",
                )
                items.append(item.as_dict())

                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["markers"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> << {api_endpoint_url} >> "
        )


def fetch_records_us(latlng, sgw):
    items = []
    total = 0
    lat, lng = latlng
    conversion_data_base_url = (
        "https://helly-hansen.locally.com/stores/conversion_data?"
    )
    input_keys = f"has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat={str(lat)}&map_center_lng={str(lng)}&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=9&lang=en-us"
    api_endpoint_url = f"{conversion_data_base_url}{input_keys}"

    try:
        r = get_response(api_endpoint_url)
        js = json.loads(r.content)["markers"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for idx, _ in enumerate(js[0:]):
                hoo = ""
                suno = ""
                if "sun_time_open" in _:
                    suno = _["sun_time_open"]
                sunc = ""
                if "sun_time_close" in _:
                    sunc = _["sun_time_close"]

                mono = ""
                if "mon_time_open" in _:
                    mono = _["mon_time_open"]
                monc = ""
                if "mon_time_close" in _:
                    monc = _["mon_time_close"]

                tueo = ""
                if "tue_time_open" in _:
                    tueo = _["tue_time_open"]
                tuec = ""
                if "tue_time_close" in _:
                    tuec = _["tue_time_close"]

                wedo = ""
                if "wed_time_open" in _:
                    wedo = _["wed_time_open"]
                wedc = ""
                if "wed_time_close" in _:
                    wedc = _["wed_time_close"]

                thuo = ""
                if "thu_time_open" in _:
                    thuo = _["thu_time_open"]

                thuc = ""
                if "thu_time_close" in _:
                    thuc = _["thu_time_close"]

                frio = ""
                if "fri_time_open" in _:
                    frio = _["fri_time_open"]
                fric = ""
                if "fri_time_close" in _:
                    fric = _["fri_time_close"]

                sato = ""
                if "sat_time_open" in _:
                    sato = _["sat_time_open"]
                satc = ""
                if "sat_time_close" in _:
                    satc = _["sat_time_close"]

                sunoc = get_hour_min_for_a_day(suno, sunc)
                monoc = get_hour_min_for_a_day(mono, monc)
                tueoc = get_hour_min_for_a_day(tueo, tuec)
                wedoc = get_hour_min_for_a_day(wedo, wedc)
                thuoc = get_hour_min_for_a_day(thuo, thuc)
                frioc = get_hour_min_for_a_day(frio, fric)
                satoc = get_hour_min_for_a_day(sato, satc)
                date_open_close = list(
                    set([sunoc, monoc, tueoc, wedoc, thuoc, frioc, satoc])
                )

                if not date_open_close:
                    hoo = "<MISSING>"
                else:
                    hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                if "Sun: , Mon: , Tue: , Wed: , Thu: , Fri: , Sat:" in hoo:
                    hoo = MISSING
                item = SgRecord(
                    locator_domain="hellyhansen.com",
                    page_url="",
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    store_number=_["id"],
                    phone=_["phone"],
                    location_type=_["slug"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation=hoo,
                    raw_address="",
                )
                items.append(item.as_dict())

                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["markers"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> << {api_endpoint_url} >> "
        )


def fetch_records_us_custom(latlng, sgw):
    items = []
    total = 0
    lat, lng = latlng
    conversion_data_base_url = (
        "https://helly-hansen.locally.com/stores/conversion_data?"
    )
    distance = "2738.497487447091"
    input_keys = f"has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat={str(lat)}&map_center_lng={str(lng)}&map_distance_diag={distance}&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4&lang=en-us&forced_coords="
    api_endpoint_url = f"{conversion_data_base_url}{input_keys}"
    try:
        r = get_response(api_endpoint_url)
        js = json.loads(r.content)["markers"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for idx, _ in enumerate(js[0:]):
                hoo = ""
                suno = ""
                if "sun_time_open" in _:
                    suno = _["sun_time_open"]
                sunc = ""
                if "sun_time_close" in _:
                    sunc = _["sun_time_close"]

                mono = ""
                if "mon_time_open" in _:
                    mono = _["mon_time_open"]
                monc = ""
                if "mon_time_close" in _:
                    monc = _["mon_time_close"]

                tueo = ""
                if "tue_time_open" in _:
                    tueo = _["tue_time_open"]
                tuec = ""
                if "tue_time_close" in _:
                    tuec = _["tue_time_close"]

                wedo = ""
                if "wed_time_open" in _:
                    wedo = _["wed_time_open"]
                wedc = ""
                if "wed_time_close" in _:
                    wedc = _["wed_time_close"]

                thuo = ""
                if "thu_time_open" in _:
                    thuo = _["thu_time_open"]

                thuc = ""
                if "thu_time_close" in _:
                    thuc = _["thu_time_close"]

                frio = ""
                if "fri_time_open" in _:
                    frio = _["fri_time_open"]
                fric = ""
                if "fri_time_close" in _:
                    fric = _["fri_time_close"]

                sato = ""
                if "sat_time_open" in _:
                    sato = _["sat_time_open"]
                satc = ""
                if "sat_time_close" in _:
                    satc = _["sat_time_close"]

                sunoc = get_hour_min_for_a_day(suno, sunc)
                monoc = get_hour_min_for_a_day(mono, monc)
                tueoc = get_hour_min_for_a_day(tueo, tuec)
                wedoc = get_hour_min_for_a_day(wedo, wedc)
                thuoc = get_hour_min_for_a_day(thuo, thuc)
                frioc = get_hour_min_for_a_day(frio, fric)
                satoc = get_hour_min_for_a_day(sato, satc)
                date_open_close = list(
                    set([sunoc, monoc, tueoc, wedoc, thuoc, frioc, satoc])
                )

                if not date_open_close:
                    hoo = "<MISSING>"
                else:
                    hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                if "Sun: , Mon: , Tue: , Wed: , Thu: , Fri: , Sat:" in hoo:
                    hoo = MISSING
                item = SgRecord(
                    locator_domain="hellyhansen.com",
                    page_url="",
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    store_number=_["id"],
                    phone=_["phone"],
                    location_type=_["slug"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation=hoo,
                    raw_address="",
                )
                items.append(item.as_dict())

                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["markers"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> << {api_endpoint_url} >> "
        )


def fetch_records_ca(latlng, sgw):
    items = []
    total = 0
    lat, lng = latlng
    conversion_data_base_url = (
        "https://helly-hansen.locally.com/stores/conversion_data?"
    )
    input_keys = f"has_data=true&company_id=58&store_mode=&style=&color=&upc=&category=Sportswear%2Bor%2Bbrandstore%2Bor%2Boutlet&inline=1&show_links_in_list=&parent_domain=&map_center_lat={str(lat)}&map_center_lng={str(lng)}&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=Canada&zoom_level=9&lang=en-us&forced_coords="
    api_endpoint_url = f"{conversion_data_base_url}{input_keys}"
    try:
        r = get_response(api_endpoint_url)
        js = json.loads(r.content)["markers"]
        logger.info(f"Pulling the data from : {r.url} ")
        if js:
            total += len(js)
            for idx, _ in enumerate(js[0:]):
                hoo = ""
                suno = ""
                if "sun_time_open" in _:
                    suno = _["sun_time_open"]
                sunc = ""
                if "sun_time_close" in _:
                    sunc = _["sun_time_close"]

                mono = ""
                if "mon_time_open" in _:
                    mono = _["mon_time_open"]
                monc = ""
                if "mon_time_close" in _:
                    monc = _["mon_time_close"]

                tueo = ""
                if "tue_time_open" in _:
                    tueo = _["tue_time_open"]
                tuec = ""
                if "tue_time_close" in _:
                    tuec = _["tue_time_close"]

                wedo = ""
                if "wed_time_open" in _:
                    wedo = _["wed_time_open"]
                wedc = ""
                if "wed_time_close" in _:
                    wedc = _["wed_time_close"]

                thuo = ""
                if "thu_time_open" in _:
                    thuo = _["thu_time_open"]

                thuc = ""
                if "thu_time_close" in _:
                    thuc = _["thu_time_close"]

                frio = ""
                if "fri_time_open" in _:
                    frio = _["fri_time_open"]
                fric = ""
                if "fri_time_close" in _:
                    fric = _["fri_time_close"]

                sato = ""
                if "sat_time_open" in _:
                    sato = _["sat_time_open"]
                satc = ""
                if "sat_time_close" in _:
                    satc = _["sat_time_close"]

                sunoc = get_hour_min_for_a_day(suno, sunc)
                monoc = get_hour_min_for_a_day(mono, monc)
                tueoc = get_hour_min_for_a_day(tueo, tuec)
                wedoc = get_hour_min_for_a_day(wedo, wedc)
                thuoc = get_hour_min_for_a_day(thuo, thuc)
                frioc = get_hour_min_for_a_day(frio, fric)
                satoc = get_hour_min_for_a_day(sato, satc)
                date_open_close = list(
                    set([sunoc, monoc, tueoc, wedoc, thuoc, frioc, satoc])
                )

                if not date_open_close:
                    hoo = "<MISSING>"
                else:
                    hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                hoo = f"Sun: {sunoc}, Mon: {monoc}, Tue: {tueoc}, Wed: {wedoc}, Thu: {thuoc}, Fri: {frioc}, Sat: {satoc}"
                if "Sun: , Mon: , Tue: , Wed: , Thu: , Fri: , Sat:" in hoo:
                    hoo = MISSING
                item = SgRecord(
                    locator_domain="hellyhansen.com",
                    page_url="",
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    store_number=_["id"],
                    phone=_["phone"],
                    location_type=_["slug"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation=hoo,
                    raw_address="",
                )
                items.append(item.as_dict())

                sgw.write_row(item)
            logger.info(
                f'Number of items found: {len(json.loads(r.content)["markers"])} : Total: {total}'
            )
        else:
            return

    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> << {api_endpoint_url} >> "
        )


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    search_us = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=1000,
        granularity=Grain_8(),
        use_state=False,
    )

    search_ca = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=1000,
        granularity=Grain_8(),
        use_state=False,
    )

    search_chl = DynamicGeoSearch(
        country_codes=[SearchableCountries.CHILE],
        expected_search_radius_miles=500,
        granularity=Grain_8(),
        use_state=False,
    )

    search_eu_fr = [(47.823607476861554, 2.6187869531297565)]
    search_us_custom = [
        (47.38579850902305, -70.4381377979114),
        (47.90492738751918, -122.67012048720358),
        (51.53443975315125, -55.34590173719422),
    ]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, latlng, sgw) for latlng in search_us
        ]
        tasks.extend(task_us)

        # Custom Latitude and Longitude
        task_us_custom = [
            executor.submit(fetch_records_us_custom, latlng, sgw)
            for latlng in search_us_custom
        ]
        tasks.extend(task_us_custom)

        task_ca = [
            executor.submit(fetch_records_ca, latlng, sgw) for latlng in search_ca
        ]
        tasks.extend(task_ca)

        task_eu_fr = [
            executor.submit(fetch_records_eu_based_on_france, latlng, sgw)
            for latlng in search_eu_fr
        ]
        tasks.extend(task_eu_fr)

        task_eu_chl = [
            executor.submit(fetch_records_eu_based_on_chile, latlng, sgw)
            for latlng in search_chl
        ]
        tasks.extend(task_eu_chl)
        for future in as_completed(tasks):
            future.result()


def scrape():

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            ),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
