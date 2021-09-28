from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = SgLogSetup().get_logger("badgercoin_com")
MISSING = SgRecord.MISSING
MAX_WORKERS = 4
LOCATION_URL = "https://www.badgercoin.com/locations"

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def get_googlemap_based_store_urls():
    with SgRequests() as http:
        r = http.get(LOCATION_URL)
        sel = html.fromstring(r.text, "lxml")
        gmapurls = sel.xpath(
            '//a[contains(@href, "goo.g") or contains(@href, "g.page")]/@href'
        )
        return gmapurls


def fetch_records(idx, gurl, http: SgRequests, sgw: SgWriter):
    locator_domain = "badgercoin.com"
    gr = http.get(gurl, headers=headers)
    gsel = html.fromstring(gr.text)
    app_options = "".join(
        gsel.xpath('//script[contains(text(), "window.APP_OPTIONS")]/text()')
    )

    meta_add_data = gsel.xpath('//meta[@itemprop="name"]/@content')
    meta_add_data = "".join(meta_add_data)
    # Location Name
    ln = meta_add_data.split("·")[0].strip()
    location_name = ln if ln else MISSING

    # Address
    add = ""
    try:

        add = meta_add_data.split("·")[1].strip()
        pai = parse_address_intl(add)
        sa = pai.street_address_1
        street_address = sa if sa else MISSING

        city = pai.city
        city = city if city else MISSING

        state = pai.state
        state = state if state else MISSING

        zip_postal = pai.postcode
        zip_postal = zip_postal if zip_postal else MISSING

    except:
        add = MISSING
        street_address = MISSING
        city = MISSING
        state = MISSING
        zip_postal = MISSING
    logger.info(f"[{idx}] st_add: {street_address}")
    logger.info(f"[{idx}] city: {city}")
    logger.info(f"[{idx}] state: {state}")
    logger.info(f"[{idx}] zip: {zip_postal}")

    # Custom address
    # https://goo.gl/maps/DZWyawYFkuygCwXE7  - The Daily Grind & Art Market
    # https://goo.gl/maps/Xpuy7ai7xuzRDiHCA - Depanneur Pointe-Claire

    if "https://goo.gl/maps/DZWyawYFkuygCwXE7" in gurl:
        location_name = "HoneyBadger Bitcoin ATM at The Daily Grind Cafe"
        add = "1479 Birmingham St, Halifax, NS B3J 1G8"
        street_address = "1479 Birmingham St"
        city = "Halifax"
        state = "NS"
        zip_postal = "B3J 1G8"

    if "https://goo.gl/maps/DZWyawYFkuygCwXE7" in gurl:
        location_name = "HoneyBadger Bitcoin ATM at Depanneur Pointe Claire"
        add = "89 Av. Ashgrove, Pointe-Claire, QC H9R 3N5"
        street_address = "89 Av. Ashgrove"
        city = "Pointe-Claire"
        state = "QC"
        zip_postal = "H9R 3N5"

    country_code = "CA"
    logger.info(f"[{idx}] country_code: {country_code}")

    store_number = MISSING
    logger.info(f"[{idx}] store_number: {store_number}")

    app_options = "".join(
        gsel.xpath('//script[contains(text(), "window.APP_OPTIONS")]/text()')
    )
    tel1 = re.findall(r"tel:\+\d+", app_options)
    tel = "".join(tel1).replace("tel:", "")
    phone = tel if tel else MISSING
    logger.info(f"[{idx}] Phone: {phone}")

    # Location Type
    location_type = MISSING
    logger.info(f"[{idx}] location_type: {location_type}")

    purl = str(gr.url)
    page_url = purl
    logger.info(f"[{idx}] Page URL: {purl}")

    # Latlng
    spotlight = app_options.split("spotlight")[-1]
    spotlight = spotlight.split("America/Vancouver")[0]
    latlng_regex_pattern = r"[-]?[\d]+[.][\d]*"
    latlng = re.findall(latlng_regex_pattern, spotlight)
    logger.info(f"Latlng: {latlng}")

    try:
        latitude = latlng[0]
    except:
        MISSING

    logger.info(f"[{idx}] lat: {latitude}")
    try:
        longitude = latlng[1]
    except:
        MISSING
    logger.info(f"[{idx}] long: {longitude}")
    hours_of_operation = ""
    try:
        hours = app_options.split("tel:")[-1]
        hours = hours.split("[[[")[2]
        hours1 = hours.split("]]")
        hours2 = [i for i in hours1 if i]
        hours3 = hours2[0:7]
        hours3 = [
            i.split('"')[1].replace("\\", "") + ": " + i.split('"')[3].replace("\\", "")
            for i in hours3
        ]
        hours_of_operation = "; ".join(hours3)

    except:
        hours_of_operation = MISSING
    if "ogs.google.com/widget/app" in hours_of_operation:
        hours_of_operation = MISSING
    logger.info(f"[{idx}] HOO: {hours_of_operation}")

    raw_address = add or MISSING

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


def fetch_records_api(http: SgRequests, sgw: SgWriter):

    r = http.get(LOCATION_URL)
    sel = html.fromstring(r.text, "lxml")
    logger.info(f"Pulling the data map id for: {LOCATION_URL}")
    data_map_id = "".join(
        sel.xpath('//div[contains(@id, "storepoint-container")]/@data-map-id')
    )
    API_ENDPOINT_URL = f"https://api.storepoint.co/v1/{data_map_id}/locations?lat=40.8&long=-73.97&radius=20000"
    locations = http.get(API_ENDPOINT_URL, headers=headers).json()["results"][
        "locations"
    ]
    for _ in locations:
        if "shore liquor" in _["name"].lower() or "meadowvale" in _["name"].lower():
            addr = _["streetaddress"].split(",")
            state = zip_postal = ""
            s_z = addr[-2].strip().split(" ")
            if len(s_z) > 2:
                state = " ".join(addr[-2].strip().split(" ")[:-2])
                zip_postal = " ".join(addr[-2].strip().split(" ")[-2:])
            else:
                state = s_z[0]
                zip_postal = s_z[-1]
            hours = []
            hours.append(f"Mon: {_['monday']}")
            hours.append(f"Tue: {_['tuesday']}")
            hours.append(f"Wed: {_['wednesday']}")
            hours.append(f"Thu: {_['tuesday']}")
            hours.append(f"Fri: {_['friday']}")
            hours.append(f"Sat: {_['saturday']}")
            hours.append(f"Sun: {_['sunday']}")
            rec = SgRecord(
                page_url=API_ENDPOINT_URL,
                store_number=_["id"],
                location_name=_["name"],
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=state,
                zip_postal=zip_postal,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                country_code="CA",
                phone=_["phone"],
                locator_domain="badgercoin.com",
                hours_of_operation="; ".join(hours),
                raw_address=_["streetaddress"],
            )
            sgw.write_row(rec)
        else:
            continue


def fetch_data(sgw: SgWriter, http: SgRequests):

    # NOTE: There are two locations which don't have
    # valid Google map URLs, therefore, we have to use API ENDPOINT URLs
    # to get the data for these locations, North Shore Liquor and Meadowvale Shopping Centre.
    # The reason for not using API ENDPOINT URL to get the data for
    # all locations is that it returns only 148 stores and seems to not upto date.

    # North Shore Liquor Store
    shore_liquor_url = "https://g.page/honeybadger-bitcoin-atm-northvan?share"

    # Mississauga - Meadowvale Shopping Centre
    meadowvale_url = "https://g.page/honeybadger-bitcoin-atm?share"
    gurls = get_googlemap_based_store_urls()
    not_shared_urls = []
    shared_urls = []

    for gu in gurls:
        if shore_liquor_url in gu:
            shared_urls.append(gu)
        elif meadowvale_url in gu:
            shared_urls.append(gu)
        else:
            not_shared_urls.append(gu)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(fetch_records, urlnum, url, http, sgw)
            for urlnum, url in enumerate(not_shared_urls[0:])
        ]
        for future in as_completed(futures):
            future.result()

    if shared_urls:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(fetch_records_api, http, sgw)]
            for future in as_completed(futures):
                future.result()


def scrape():
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_data(writer, http)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
