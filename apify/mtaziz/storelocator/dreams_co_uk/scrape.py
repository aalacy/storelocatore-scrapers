from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("dreams_co_uk")
DOMAIN = "dreams.co.uk"
MISSING = SgRecord.MISSING
MAX_WORKERS = 5

headers_c = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers_c)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTPErrorCode: {response.status_code}")


def fetch_records(snum, store_name, sgw: SgWriter):
    try:
        api_url = (
            f"https://www.dreams.co.uk/store-finder?q={store_name}&page=0&productCode="
        )
        r = get_response(api_url)
        sel = html.fromstring(r.text, "lxml")
        xpath_alert = (
            '//div[contains(@class, "alert alert-danger alert-dismissable")]/text()'
        )
        alert_msg = "".join(sel.xpath(xpath_alert))
        if "Check that you" in alert_msg:
            logger.info("Store data is not available")
            return
        else:
            logger.info("The data is available")
            data = r.json()
            json_data = data["data"]
            for j in json_data:
                location_name = j["displayName"] or MISSING
                # Newry Bed Store store URL does not work therefore, it's dropped
                if "Newry Bed Store" in location_name:
                    return

                # Page URL
                name = j["name"] or MISSING
                store_locator_url = "https://www.dreams.co.uk/store/"
                page_url = f"{store_locator_url}{name}"
                logger.info(f"[{snum}][{store_name}] Page URL: {page_url}")

                sta = ""
                sta1 = j["line1"]
                sta2 = j["line2"]
                if sta1 and sta2:
                    sta = sta1 + ", " + sta2
                elif sta1 and not sta2:
                    sta = sta1
                elif not sta1 and sta2:
                    sta = sta2
                else:
                    sta = MISSING
                if MISSING not in sta:
                    if "Unit" in sta and len(sta) < 12:
                        r1 = get_response(page_url)
                        logger.info(f"Pulling StreetAddress from: {page_url}")
                        sel = html.fromstring(r1.text, "lxml")
                        add_js = sel.xpath(
                            '//script[contains(@type, "application/ld+json") and contains(text(), "LocalBusiness")]/text()'
                        )
                        add_js = json.loads("".join(add_js))
                        sta = add_js["address"]["streetAddress"].replace("amp;", "")

                city = ""
                c = j["town"]
                if c:
                    city = c
                else:
                    if "Wembley Bed Store" in location_name:
                        city = "Wembley"
                    elif "West Ealing Bed Store" in location_name:
                        city = "West Ealing"
                    elif "Perth Bed Store" in location_name:
                        city = "Perth"
                    else:
                        city = MISSING

                state = MISSING
                zip_postal = j["postalCode"] or MISSING
                country_code = "GB"
                phone = j["phone"] or MISSING
                lat = j["latitude"] or MISSING
                lng = j["longitude"] or MISSING
                hours = []
                for i in j["openings"]:
                    day = i["day"]
                    ot = i["openingTime"]
                    ct = i["closingTime"]
                    day_ot_ct = f"{day} {ot} - {ct}"
                    hours.append(day_ot_ct)
                hoo = "; ".join(hours)

                location_type = ""
                if "features" in j:
                    features = j["features"]
                    features = [i["name"] for i in features]
                    location_type = ", ".join(features)
                else:
                    location_type = MISSING
                item = SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=sta,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=location_type,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hoo,
                    raw_address=MISSING,
                )
                sgw.write_row(item)
    except Exception as e:
        logger.info(f"Fix FetchRecordsError: << {e} >> at {store_name}")


def get_slug_list():
    sitemap_url = "https://www.dreams.co.uk/store-finder/sitemap"
    r1 = get_response(sitemap_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator__link = '//a[contains(@class, "store-locator__link")]/text()'
    all_stores = sel1.xpath(xpath_store_locator__link)
    slug_list = []
    for i in all_stores:
        j = i.replace(" - ", "-").strip().lower()
        k = j.replace(" ", "-").replace("(", "").replace(")", "")
        slug_list.append(k)
    return slug_list


def fetch_data(sgw: SgWriter):
    store_names = get_slug_list()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, snum, storename, sgw)
            for snum, storename in enumerate(store_names[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
