# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re


website = "pizzahut.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers_ = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}

headers = {
    "authority": "store.prod.pizzahutaustralia.com.au",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_google_map_url(code_id):
    based_on_id_api_url = f"https://api.storyblok.com/v1/cdn/stories?starts_with=stores%2F&filter_query%5Bstore.store.code%5D%5Bin%5D={code_id}&version=published&cv=1648060623404&token=HgBCt0Zyhy4FvUyBjroBwgtt"
    with SgRequests() as s1:
        r1 = s1.get(based_on_id_api_url, headers=headers_)
        js = json.loads(r1.text)
        contents = js["stories"]
        google_map_detailed_url = ""
        google_map_tiny_url = ""
        if contents:
            snippet = contents[0]["content"]["bottom_snippet"]
            raw_links_containing_gmap = re.findall(r"\((.*)\)", snippet)
            gmaps = [i for i in raw_links_containing_gmap if "/maps/" in i]
            log.info(f"gmaps: {gmaps}")
            for gmap in gmaps:
                if "https://www.google.com/maps/place" in gmap:
                    google_map_detailed_url = gmap
                    log.info(f"Google Map Detailed URL: {google_map_detailed_url}")
                else:
                    if "goo.gl/maps" in gmap:
                        gmap_tiny = gmap.split(")")[0]
                        google_map_tiny_url = "".join(gmap_tiny)

                        log.info(f"Gmap Tiny URL: {google_map_tiny_url}")
                        with SgRequests() as s_tiny:
                            s_tiny = SgRequests()
                            r_tiny = s_tiny.get(google_map_tiny_url)
                            google_map_detailed_url = str(r_tiny.url)
                    else:
                        log.info("Google URL is not Available")
                        google_map_detailed_url = ""
    return google_map_detailed_url


def get_latlng(map_link):
    latitude = ""
    longitude = ""
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://store.prod.pizzahutaustralia.com.au/api/v1/store?includeComingSoon=false"
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)
        for idx, store in enumerate(stores[0:]):
            store_name = store["name"].replace(" ", "-")
            page_url = f"https://www.pizzahut.com.au/stores/pizza-hut-{store_name}"
            log.info(page_url)
            api_url = f"https://store.prod.pizzahutaustralia.com.au/api/v1/store/name?name={store['name']}"
            with SgRequests() as session2:
                store_req = session2.get(api_url, headers=headers)
                if store_req.status_code == 200:
                    store_json = json.loads(store_req.text)["store"]
                    code_id = store_json["code"]
                    google_map_url = get_google_map_url(code_id)
                    lat = ""
                    lng = ""
                    if google_map_url:
                        lat, lng = get_latlng(str(google_map_url))
                    else:
                        lat = ""
                        lng = ""
                    location_name = store_json["name"]
                    location_type = store_json["storeType"]
                    locator_domain = website

                    street_address = store_json["addressLine1"]
                    if store_json["addressLine2"]:
                        street_address = (
                            street_address + ", " + store_json["addressLine2"]
                        )
                    city = store_json["city"]
                    state = store_json["state"]
                    zip_ = store_json["postCode"]

                    country_code = store_json["country"]
                    store_number = store_json["code"]
                    phone = store_json["telephone"]
                    hours_list = []
                    hours = json.loads(store_req.text)["tradingDays"]

                    for hour in hours:
                        day = hour["displayDate"]
                        time = (
                            hour["tradingHours"][0]["openingTime"]
                            + "-"
                            + hour["tradingHours"][0]["closingTime"]
                        )
                        hours_list.append(day + ": " + time)

                    hours_of_operation = "; ".join(hours_list)
                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours_of_operation,
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
