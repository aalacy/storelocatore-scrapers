from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import tenacity


logger = SgLogSetup().get_logger("pandaexpress_com")
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
}

MAX_WORKERS = 10


def get_states():
    url = "https://www.pandaexpress.com/locations"
    states = []
    with SgRequests() as session:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<a class="record" href="/locations/' in line:
                items = line.split('<a class="record" href="/locations/')
                for item in items:
                    if 'data-ga-event="locationClick' in item:
                        lurl = (
                            "https://www.pandaexpress.com/locations/"
                            + item.split('"')[0]
                        )
                        states.append(lurl)
        logger.info(f"#OFSTATE: {len(states)}")
    return states


def get_locs_cities():
    states = get_states()
    cities = [
        "https://www.pandaexpress.com/locations/wi/milwaukee",
        "https://www.pandaexpress.com/locations/tx/hurst",
        "https://www.pandaexpress.com/locations/sc/charleston",
        "https://www.pandaexpress.com/locations/sc/myrtle-beach",
        "https://www.pandaexpress.com/locations/mi/lansing",
        "https://www.pandaexpress.com/locations/mi/rochester",
        "https://www.pandaexpress.com/locations/md/frederick",
        "https://www.pandaexpress.com/locations/in/lafayette",
        "https://www.pandaexpress.com/locations/il/peoria",
        "https://www.pandaexpress.com/locations/ia/des-moines",
        "https://www.pandaexpress.com/locations/hi/kailua",
        "https://www.pandaexpress.com/locations/fl/panama-city",
        "https://www.pandaexpress.com/locations/ca/covina",
        "https://www.pandaexpress.com/locations/ca/highland",
        "https://www.pandaexpress.com/locations/ca/hollywood",
        "https://www.pandaexpress.com/locations/ca/monterey",
        "https://www.pandaexpress.com/locations/ca/walnut",
        "https://www.pandaexpress.com/locations/ca/woodland",
        "https://www.pandaexpress.com/locations/az/prescott",
        "https://www.pandaexpress.com/locations/ar/benton",
    ]
    locs = ["https://www.pandaexpress.com/locations/ar/benton/20810-i-30-north"]
    with SgRequests() as session:
        logger.info(f"#OFSTATE: {len(states)}")

        # UPPER LIMIT OF STATES NEEDS TO BE UPDATED ON PROD
        for sidx, state in enumerate(states[0:]):
            logger.info(f"[{sidx}, {state} ]")
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if '<a class="record" href="/locations/' in line2:
                    items = line2.split('<a class="record" href="/locations/')
                    for item in items:
                        if 'data-ga-event="locationClick"' in item:
                            lurl = (
                                "https://www.pandaexpress.com/locations/"
                                + item.split('"')[0]
                            )
                            lurl = lurl.replace("coeur-dalene", "coeur-d'alene")
                            if "(1) </a>" in item and lurl not in cities:
                                locs.append(lurl)
                            else:
                                cities.append(lurl)
    return locs, cities


def get_loc_single(cidx, city, session: SgRequests):
    logger.info(f"[{cidx}, {city} ]")
    r3 = session.get(city, headers=headers)
    for line2 in r3.iter_lines():
        if '<a href="/locations/' in line2:
            items = line2.split('<a href="/locations/')
            for item in items:
                if 'data-ga-event="storeDetailsClick"' in item:
                    lurl = (
                        "https://www.pandaexpress.com/locations/" + item.split('"')[0]
                    )
                    return lurl


def fetch_store_url():
    locs2, cities = get_locs_cities()
    logger.info(f"[#CITIES: {len(cities)}]")
    with SgRequests() as session:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = []
            # UPPER LIMIT OF CITIES NEEDS TO BE UPDATED ON PROD
            store_data = [
                executor.submit(get_loc_single, storenum, city, session)
                for storenum, city in enumerate(cities[0:])
            ]
            tasks.extend(store_data)
            for future in as_completed(tasks):
                record = future.result()
                if record is not None or record:
                    locs2.append(record)
    return locs2


@tenacity.retry(
    reraise=True,
    stop=tenacity.stop_after_attempt(2),
    wait=tenacity.wait_random(min=0, max=5),
)
def get_response(url):
    with SgRequests() as http:
        r = http.get(url, headers=headers)
        logger.info(f"GetResponse: {url}")
        if r.status_code == 200:
            logger.info(f"[GetResponseHTTP {r.status_code} OK!]")
            return r
        raise Exception(f"{url} >> TemporaryError: HTTPSTATUS: {r.status_code}")


def get_store_number(url):
    with SgRequests() as http:
        r = http.get(url, headers=headers)
        if r.status_code == 200:
            logger.info(f"[API HTTP {r.status_code} OK!]")
            return r
        raise Exception(f"{url} >> FIX STORENUMBERERROR: {r.status_code}")


def fetch_records(lid, loc, sgw: SgWriter):
    try:
        loc = loc.replace("coeur-dalene", "coeur-d'alene")
        logger.info(f"[{lid}] [PULLINGFROM] {loc}")
        try:
            r2 = get_response(loc)
        except:
            return
        if r2 is not None:

            # Get store number and latitude and longitude data from API response.
            # This part is special, it took me a lot of effort to get this API endpoint.
            sel20 = html.fromstring(r2.text)
            typ = "<MISSING>"
            hours = ""
            add = ""
            store_number = ""
            latitude = ""
            longitude = ""
            country = "US"
            phone = ""
            phone1 = ""
            phone2 = ""

            slug20 = sel20.xpath("//@data-productlink")
            if slug20:
                slug = slug20[0].split("/")[2]
                if slug:
                    logger.info(f"[SLUG {slug} ]")
                    api_endpoint_url = f"https://nomnom-prod-api.pandaexpress.com/restaurants/byslug/{slug}"
                    r21 = get_store_number(api_endpoint_url)
                    js21 = r21.json()
                    store_number = js21["extref"]
                    latitude = js21["latitude"]
                    longitude = js21["longitude"]
                    country = js21["country"]
                    phone1 = js21["telephone"]
                else:
                    storeid = "".join(
                        sel20.xpath('//a[contains(@href, "storeid=")]/@href')
                    )
                    if storeid:
                        # Please on the source page for each store, it does not contain,
                        # storeid data, which leads to use alternative solution
                        # Example URL containing store id https://orders.pandaexpress.com/mp/pub/start?storeid=2010
                        store_number = storeid.split("storeid=")[-1]
                    else:
                        store_number = ""
            else:
                storeid = "".join(sel20.xpath('//a[contains(@href, "storeid=")]/@href'))
                if storeid:
                    # Please on the source page for each store, it does not contain,
                    # storeid data, which leads to use alternative solution
                    # Example URL containing store id https://orders.pandaexpress.com/mp/pub/start?storeid=2010
                    store_number = storeid.split("storeid=")[-1]
                else:
                    store_number = ""

            for line2 in r2.iter_lines():
                if '<div class="phone"><a href="tel:' in line2:
                    phone2 = line2.split('<div class="phone"><a href="tel:')[1].split(
                        '"'
                    )[0]

                if '<link rel="canonical" href="' in line2:
                    purl = line2.split('<link rel="canonical" href="')[1].split('"')[0]
                if '<div class="name"><h2>' in line2:
                    name = (
                        line2.split('<div class="name"><h2>')[1]
                        .split("<")[0]
                        .replace("&amp;", "&")
                    )
                if '<div class="address">' in line2 and add == "":
                    address = line2.split('<div class="address">')[1].split("</div>")[0]
                    add = address.split("<br>")[0].strip()
                    city = address.split("<br>")[1].strip().split(",")[0]
                    state = (
                        address.split("<br>")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .rsplit(" ", 1)[0]
                    )
                    zc = address.strip().rsplit(" ", 1)[1]
                    rawadd = address.replace("<br>", ", ").replace("  ", " ")
                try:
                    if '<div class="day_name">' in line2:
                        days = line2.split('<div class="day_name">')
                        for day in days:
                            if '<div class="day_hours">' in day:
                                hrs = (
                                    day.split("<")[0]
                                    + ": "
                                    + day.split('<div class="day_hours">')[1].split(
                                        "<"
                                    )[0]
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                except:
                    hours = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if (
                "," in add
                and "Km " not in add
                and "Lot " not in add
                and "Int. " not in add
                and "Pr2" not in add
                and "Pr-3" not in add
                and "Suite" not in add
            ):
                addnew = add.split(",")[1].strip()
                if len(addnew) <= 2:
                    add = add.replace(",", "")
                else:
                    add = addnew
            if phone1:
                phone = phone1
            if phone2:
                phone = phone2
            if len(zc) >= 1:
                item = SgRecord(
                    locator_domain="pandaexpress.com",
                    page_url=purl,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store_number,
                    latitude=latitude,
                    longitude=longitude,
                    raw_address=rawadd,
                    hours_of_operation=hours,
                )
                sgw.write_row(item)
    except Exception as e:
        logger.info(f"[PLEASE FIX FETCHRECORDSERROR << {e} >> | {loc} | {lid}]")
        return


def fetch_data(sgw: SgWriter):
    logger.info("Scrape Started")
    store_urls_thrd = fetch_store_url()
    logger.info("Store URLs Scraped!")
    # This store count may not be actual as some of the store urls
    # might not be working, so we will ignore those.

    logger.info(f"Total Stores: {len(store_urls_thrd)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        # UPPER LIMIT OF STORES_URLS_THRD NEEDS TO BE UPDATED ON PROD

        store_data = [
            executor.submit(fetch_records, storenum, url, sgw)
            for storenum, url in enumerate(store_urls_thrd[0:])
        ]
        tasks.extend(store_data)
        for future in as_completed(tasks):
            record = future.result()
            if record is not None or record:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
