import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.bp.com"
page_url = "https://www.bp.com/en_us/united-states/home/find-a-gas-station.html"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_all_coord(co_ord):
    url = f"https://bpretaillocator.geoapp.me/api/v1/locations/within_bounds?sw[]={co_ord[0]}&sw[]={co_ord[1]}&ne[]={co_ord[2]}&ne[]={co_ord[3]}&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=5&unit_system=1&format=json"
    with SgRequests() as session:

        response = session.get(url, headers=headers)
        if response.status_code != 200:
            log.error(f" can't fetch = {response.status_code} = > {co_ord}")
            return []
        data = []
        coords = json.loads(response.text)

        for coord in coords:
            co_ord = [
                coord["bounds"]["sw"][0],
                coord["bounds"]["sw"][1],
                coord["bounds"]["ne"][0],
                coord["bounds"]["ne"][1],
                coord["size"],
            ]
            size = coord["size"]
            if size > 300:
                data += fetch_all_coord(co_ord)
            else:
                data.append(co_ord)
    return data


def fetch_single_co_ord(coord, retry=1):
    url = f"https://bpretaillocator.geoapp.me/api/v1/locations/within_bounds?sw[]={coord[0]}&sw[]={coord[1]}&ne[]={coord[2]}&ne[]={coord[3]}&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=5&unit_system=1&format=json"
    with SgRequests() as session:
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            if retry == 3:
                log.error(f" can't fetch = {response.status_code} = > {coord}")
                return coord, []
            else:
                log.warn(
                    f" can't fetch = {response.status_code} = > {coord}; sleeping for 5m"
                )
                time.sleep(5 * 60)
                return fetch_single_co_ord(coord, retry + 1)
        stores = json.loads(response.text)
    return coord, stores


def fetch_data():
    coords = fetch_all_coord([-89, -179, 89, 179])
    log.info(f"Total co ordinates = {len(coords)}")

    count = 0
    store_added = 0
    for coord in coords:
        coord, stores = fetch_single_co_ord(coord)
        count = count + 1
        log.debug(f"{count}. stores = {len(stores)}")

        for store in stores:
            location_name = store.get("name")
            store_number = store.get("id")
            location_type = store.get("site_brand")
            street_address = store.get("address")
            city = store.get("city")
            state = store.get("state")
            postal = store.get("postcode") or ""
            if "-" in postal:
                postal = MISSING
            country_code = store.get("country_code")
            phone = store.get("telephone")
            latitude = store.get("lat")
            longitude = store.get("lng")

            _tmp = []
            hours = store.get("opening_hours") or []
            for h in hours:
                days = h.get("days") or []
                inters = h.get("hours") or []
                try:
                    _tmp.append(f'{"-".join(days)}: {"-".join(inters[0])}')
                except:
                    pass

            hours_of_operation = ";".join(_tmp)

            store_added = store_added + 1
            yield SgRecord(
                locator_domain=website,
                page_url=page_url,
                store_number=store_number,
                location_type=location_type,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
    log.info(f"Total stores added {store_added}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {(end-start)/60} minutes.")


if __name__ == "__main__":
    scrape()
