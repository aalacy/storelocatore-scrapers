from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import json


logger = SgLogSetup().get_logger("circlek_com__qualityguaranteed")

MAX_WORKERS = 10
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_api_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_flatten_data_list(data):
    # This returns flatten data list contains page urls
    # and using the page urls from API response,
    # store data will be obtained from the response from page_url

    data_flatten = []
    for k, v in data.items():
        d1 = {}
        for k1, v1 in data[k].items():
            if k1 == "services":
                sname = [i["display_name"] for i in v1]
                d1["sname"] = ", ".join(sname)
            if k1 == "url":
                d1["page_url"] = "https://www.circlek.com" + v1
            d1[k1] = v1
        del d1["services"]
        del d1["url"]
        data_flatten.append(d1)
    return data_flatten


def fetch_api_res(api_page_num):
    location_url = f"https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000&services=gas,diesel&region=global&page={api_page_num}&limit=300"
    logger.info(f"Pulling data & Store URLs from API: {location_url} ")
    r = get_api_response(location_url)
    stores = r.json()["stores"]
    flatten_data = None
    if stores:
        flatten_data = get_flatten_data_list(stores)
    else:
        return
    return flatten_data


def fetch_data_from_api_res(start_pn, end_pn):
    data_list = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_api_res = [
            executor.submit(fetch_api_res, api_pgnum)
            for api_pgnum in range(start_pn, end_pn)
        ]
        tasks.extend(task_api_res)
        for future in as_completed(tasks):
            record = future.result()
            if record is not None or record:
                data_list.extend(record)
    return data_list


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_purl_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_hoo(store_sel):
    hours = store_sel.xpath(
        '//div[@class="columns large-12 middle hours-wrapper"]/div[contains(@class,"hours-item")]'
    )
    hours_list = []
    for hour in hours:
        day = "".join(hour.xpath("span[1]/text()")).strip()
        time = "".join(hour.xpath("span[2]/text()")).strip()
        hours_list.append(day + ":" + time)
    hours_of_operation = "; ".join(hours_list).strip()
    return hours_of_operation


def get_locname(ddict, store_json):
    location_name = ""
    location_name = (
        store_json.get("description").split(",")[0]
        or ddict.get("display_brand")
        or ddict.get("store_brand")
        or ddict.get("name")
        or "<MISSING>"
    )
    location_name = location_name.replace("&#039;", "'").replace("amp;", "").strip()

    if location_name == "Circle K at":
        location_name = "Circle K"
    location_name = location_name.replace("Visit your local", "").strip()

    return location_name


def get_sta(store_json):
    street_address = ""
    street_address = (
        store_json["address"]["streetAddress"]
        .replace("  ", " ")
        .replace("&#039;", "'")
        .replace("&amp;", "&")
        .strip()
    )
    if street_address[-1:] == ",":
        street_address = street_address[:-1]
    return street_address


def get_rawadd(store_sel):
    raw_address = (
        "".join(store_sel.xpath('//h1[@class="heading-big"]//text()'))
        .strip()
        .replace("Circle K,", "")
        .strip()
        + ","
        + "".join(store_sel.xpath('//h2[@class="heading-small"]//text()')).strip()
    )
    raw_address = " ".join(raw_address.split())
    raw_address = raw_address.lstrip(",").strip()
    raw_address = [i.strip() for i in raw_address.split(",")]
    raw_address = ", ".join(raw_address)
    return raw_address


def fetch_details(item_num, data_dict, sgw: SgWriter):
    logger.info(f"[{item_num}] Pulling the data from {data_dict['page_url']} ")  # noqa
    locator_domain = "circlek.com/qualityguaranteed"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip_postal = ""
    country_code = ""
    store_number = data_dict["cost_center"]
    phone = ""
    location_type = data_dict["store_brand"]
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = data_dict["page_url"]
    raw_address = ""
    if data_dict["op_status"] == "Planned":
        street_address = data_dict["address"]
        city = data_dict["city"]
        state = data_dict["division_name"]
        if state is not None:
            state = state.replace("franchise", "")
        country_code = data_dict["country"]
        if MISSING not in street_address:
            location_name = "Circle K at" + " " + street_address
        else:
            location_name = "Circle K"
        latitude = data_dict["latitude"]
        longitude = data_dict["longitude"]
        hours_of_operation = "Coming Soon"

        rec = SgRecord(
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
        sgw.write_row(rec)
    else:
        store_res = get_purl_response(page_url)
        store_sel = html.fromstring(store_res.text)
        json_list = store_sel.xpath(
            '//script[contains(@type, "application/ld+json") and contains(text(), "gasStation")]/text()'
        )
        if not json_list:
            rec = SgRecord(
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
                raw_address="<MISSING>",
            )
            sgw.write_row(rec)
        else:
            js1 = "".join(json_list)
            js2 = " ".join(js1.split())
            js3 = js2.replace("}, ]", "}]")
            store_json = json.loads(js3)
            location_name = get_locname(data_dict, store_json)
            ln1 = location_name.split(" ")[0]
            if ln1 == "at":
                location_name = "Circle K " + location_name

            phone = store_json["telephone"]
            street_address = get_sta(store_json)
            city = (
                store_json["address"]["addressLocality"].replace("&#039;", "'").strip()
            )
            if not city and data_dict["city"]:
                city = data_dict["city"]
            if not city and not data_dict["city"]:
                city = ""

            state = ""
            zip_postal = store_json["address"]["postalCode"].strip()
            country_code = data_dict["country"]
            if not country_code:
                country_code = page_url.split("https://www.circlek.com/store-locator/")[
                    -1
                ].split("/")[0]

            # Latitude
            latitude = store_json["geo"]["latitude"].replace(",", ".")
            if not latitude and data_dict["latitude"]:
                latitude = data_dict["latitude"]
            if not latitude and not data_dict["latitude"]:
                latitude = ""
            if "0.0000000" in latitude:
                latitude = ""

            # Longitude
            longitude = store_json["geo"]["longitude"].replace(",", ".")
            if not longitude and data_dict["longitude"]:
                longitude = data_dict["longitude"]

            if not longitude and not data_dict["longitude"]:
                longitude = ""
            if "0.0000000" in longitude:
                longitude = ""

            logger.info(f"Latitude: {latitude} | Longitude: {longitude} | {page_url} ")
            rawadd = ""

            raw_address = get_rawadd(store_sel)
            logger.info(f"Length of raw address: {len(raw_address)}")

            # If comma or comma with space found then replaced with <MISSING>
            if raw_address == "," or raw_address.strip() == ",":
                rawadd = MISSING
            else:
                rawadd = raw_address
            formatted_addr = parse_address_intl(raw_address)
            state = formatted_addr.state
            if state:
                state = state.replace("Mills", "").replace("Est", "").strip()
            if country_code.lower()[:2] == "ca" and state == "CA":
                state = ""
            if state == "ON":
                country_code = "Canada"
            if state is not None:
                state = state.replace("franchise", "")
            hours_of_operation = get_hoo(store_sel)
            rec = SgRecord(
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
                raw_address=rawadd,
            )
            sgw.write_row(rec)


def fetch_data(sgw: SgWriter):

    # The API Endpoint
    # If ( services="" ) considered to be empty then
    # we can get all store urls across the world
    # from API response.

    # API call only returns 10 items per page, given that
    # maximum number of items found to be around 9600 across the globe.
    # Each API response returns 10 items, total 960 API calls
    # to be made to get all the stores.
    # Start Page Number: 0
    # End Page Number: 980
    # PROD
    START_PAGENUM = 0
    END_PAGENUM = 340

    data_from_api = fetch_data_from_api_res(START_PAGENUM, END_PAGENUM)
    logger.info("API endpoints urls page_url extraction done!!")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        store_data = [
            executor.submit(fetch_details, storenum, data_frmapi, sgw)
            for storenum, data_frmapi in enumerate(data_from_api[0:])
        ]
        tasks.extend(store_data)
        for future in as_completed(tasks):
            record = future.result()
            if record is not None or record:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
