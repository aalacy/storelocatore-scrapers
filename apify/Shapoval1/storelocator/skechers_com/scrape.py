import time
import json
from concurrent import futures

from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "https://www.skechers.com/"
store_url = "https://hosted.where2getit.com/skechers/rest/locatorsearch?like=0.2986525278541239&lang=en_US"
MISSING = SgRecord.MISSING
max_workers = 4

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(coord):
    lat, long = coord

    data = (
        '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"geoip":false,"dataview":"store_default","order":"_distance","limit":1000,"geolocs":{"geoloc":[{"addressline":"","country":"","latitude":"'
        + str(lat)
        + '","longitude":"'
        + str(long)
        + '","state":"","province":"","city":"","address1":"","postalcode":""}]},"searchradius":"250","where":{"expdate":{"ge":"2021-94"},"authorized":{"distinctfrom":"1"},"or":{"retail":{"eq":""},"outlet":{"eq":""},"warehouse":{"eq":""},"apparel_store":{"eq":""},"curbside_pickup":{"eq":""},"reduced_hours":{"eq":""},"in_store_pickup":{"eq":""},"promotions":{"eq":""}}},"false":"0"}}}'
    )

    try:
        response = session.post(store_url, headers=headers, data=data)
        stores = json.loads(response.text)["response"]["collection"]
        log.debug(f"From {coord} stores = {len(stores)}")
        return stores
    except Exception as e:
        log.error(f"can't able to get data from {coord}: {e}")
        return []


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_object(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
        if value is None:
            return noVal
    return value


def fetch_data():
    for country_code in SearchableCountries.ALL:
        coords = DynamicGeoSearch(
            country_codes=[f"{country_code}"], max_search_distance_miles=10
        )

        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executors = {
                executor.submit(request_with_retries, coord): coord for coord in coords
            }

            for future in futures.as_completed(executors):
                stores = future.result()
                for j in stores:
                    page_url = "https://www.skechers.com/store-locator.html"
                    location_name = "Skechers"
                    street_address = (
                        f"{j.get('address1')} {j.get('address2')}".replace("None", "")
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )

                    state = j.get("state") or j.get("province") or "<MISSING>"
                    postal = j.get("postalcode") or "<MISSING>"
                    country_code = j.get("country") or "<MISSING>"
                    city = j.get("city") or "<MISSING>"
                    store_number = j.get("storeid") or "<MISSING>"
                    latitude = j.get("latitude") or "<MISSING>"
                    if latitude == "<MISSING>":
                        continue
                    longitude = j.get("longitude") or "<MISSING>"
                    phone = j.get("phone") or "<MISSING>"
                    hours_of_operation = (
                        f"Mon {j.get('rmon')} Tue {j.get('rtues')} Wed {j.get('rwed')} Thur {j.get('rthurs')} Fri {j.get('rfri')} Sat {j.get('rsat')} Sun {j.get('rsun')}"
                        or "<MISSING>"
                    )
                    if hours_of_operation.count("None") == 7:
                        hours_of_operation = "<MISSING>"
                    if (
                        hours_of_operation.count("CLOSED") == 7
                        or hours_of_operation.count("Closed") == 7
                    ):
                        hours_of_operation = "Closed"

                    yield SgRecord(
                        locator_domain=website,
                        store_number=store_number,
                        page_url=page_url,
                        location_name=location_name,
                        location_type=MISSING,
                        street_address=street_address,
                        city=city,
                        zip_postal=postal,
                        state=state,
                        country_code=country_code,
                        phone=phone,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=MISSING,
                    )
    return []


def scrape():
    CrawlStateSingleton.get_instance().save(override=True)
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
