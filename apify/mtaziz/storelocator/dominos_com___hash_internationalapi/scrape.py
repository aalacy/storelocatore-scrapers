from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import random

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


MISSING = SgRecord.MISSING
DOMAIN = "dominos.com"
MAX_WORKERS = 10
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com___hash_internationalapi")

searchurls = [
    "BRAZIL|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=BR&latitude=-13.5415477&longitude=-56.3346976&radius=9999999",
    "ARUBA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=AW&latitude=12.5175281&longitude=-70.0357333&radius=9999999",
    "CAYMAN_ISLANDS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KY&latitude=19.3300248&longitude=-81.3224693&radius=9999999",
    "COLOMBIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=CO&latitude=4.5709&longitude=-74.2973&Radius=1250000&radius=9999999",
    "DOMINICAN_REPUBLIC|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=DO&latitude=19.022717&longitude=-70.998641&radius=9999999",
    "ECUADOR|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=EC&latitude=-0.177491&longitude=-78.599166&radius=9999999",
    "GUATEMALA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GT&latitude=15.3430079&longitude=-90.0663352&radius=9999999",
    "PANAMA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=PA&latitude=8.3999404&longitude=-80.6812235&radius=9999999",
    "ST_KITTS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KN&latitude=17.3021931&longitude=-62.7323442&radius=9999999",
    "ST_LUCIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=LC&latitude=13.909444&longitude=-60.97889299999997&radius=9999999",
    "ST_MAARTEN|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=SX&latitude=18.0472401&longitude=-63.0887697&radius=9999999",
    "TRINIDAD|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=TT&latitude=10.536421&longitude=-61.311951&radius=9999999",
    "AUSTRIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AT&latitude=48.262853&longitude=16.399944&radius=9999999",
    "CZECH_REPUBLIC|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=CZ&latitude=49.1938084&longitude=16.6076158&radius=9999999",
    "ITALY|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=IT&latitude=45.4654219&longitude=9.18592430000001&radius=9999999",
    "KOSOVO|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=XK&latitude=42.665411916980034&longitude=21.158615201711655&radius=9999999",
    "PORTUGAL|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PT&latitude=38.740335&longitude=-9.1833424&radius=9999999",
    "SLOVAKIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SK&latitude=48.14816&longitude=17.10674&radius=9999999",
    "SWEDEN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SE&latitude=55.5700886&longitude=12.8758906&radius=9999999",
    "UAE|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AE&latitude=25.234213&longitude=55.235698&radius=9999999",
    "CAMBODIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=KH&latitude=12.2927611&longitude=103.8567493&radius=9999999",
    "GUAM|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GU&latitude=13.444304&longitude=144.79373099999998&radius=9999999",
    "PHILIPPINES|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PH&latitude=14.599512&longitude=120.984222&Radius=2500&radius=9999999",
    "THAILAND|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=TH&latitude=13.499307&longitude=100.511436&radius=9999999",
    "BAHRAIN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=BH&latitude=26.250747&longitude=50.665052&radius=9999999",
    "EGYPT|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=EG&latitude=26.820553&longitude=30.802498000000014&radius=9999999",
    "JORDAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=JO&latitude=32.2831971&longitude=35.8949949&radius=9999999",
    "LEBANON|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=LB&latitude=33.8886289&longitude=35.49547940000002&radius=9999999",
    "MAURITIUS|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=MU&latitude=-20.3484&longitude=57.5522&radius=9999999",
    "OMAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=OM&latitude=20.391015&longitude=56.8505923&radius=9999999",
    "QATAR|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=QA&latitude=25.4477038&longitude=51.1814573&radius=9999999",
]


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_global(idx, url, headers_custom):
    with SgRequests() as http:
        response = http.get(url, headers=headers_custom)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def fetch_records_global(idx, url, sgw: SgWriter):
    lurl = url.split("|")[1]
    cc = url.split("|")[0]
    headers2 = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "DPZ-Market": cc,
    }

    r = get_response_global(idx, lurl, headers2)
    time.sleep(2)
    website = "dominos.com"
    typ = MISSING
    country = lurl.split("regionCode=")[1].split("&")[0]
    loc = MISSING
    store = MISSING
    hours = MISSING
    lat = MISSING
    lng = MISSING
    logger.info("Pulling Stores")
    for idx2, item in enumerate(json.loads(r.content)["Stores"][0:]):
        if "StoreName" in str(item):
            name = item["StoreName"]
        else:
            name = MISSING

        store = item["StoreID"]
        phone = ""
        if "Phone" in item:
            phone = item["Phone"]
        else:
            phone = MISSING
        phone = phone if phone else MISSING
        logger.info(f"[{idx}][{cc}][{idx2}] phone: {phone}")
        try:
            add = item["StreetName"]
        except:
            add = MISSING
        add = str(add).replace("\r", "").replace("\n", "")
        city = ""
        if "City" in item:
            city = str(item["City"]).replace("\r", "").replace("\n", "")
        else:
            city = MISSING
        city = city if city else MISSING

        state = ""
        if "Region" in item:
            state = item["Region"] if item["Region"] else MISSING
        else:
            state = MISSING

        zc = ""
        if "PostalCode" in item:
            zc = item["PostalCode"]
        else:
            zc = MISSING

        if "MISSING" not in zc:
            j = zc.replace("-", "")
            if str.isdigit(j) is False:
                zc = MISSING
            else:
                zc = zc

        if zc == "" or zc is None:
            zc = MISSING

        if "StoreCoordinates" in item and "StoreLatitude" in item["StoreCoordinates"]:
            lat = item["StoreCoordinates"]["StoreLatitude"]
            lng = item["StoreCoordinates"]["StoreLongitude"]
        elif "Latitude" in item:
            lat = item["Latitude"]
            lng = item["Longitude"]
        else:
            lat = MISSING
            lng = MISSING

        logger.info(f"[{idx}][{cc}][{idx2}] Latlng: {lat} | {lng}")

        hours = ""
        if "HoursDescription" in item:
            hours = (
                str(item["HoursDescription"])
                .replace("\t", "")
                .replace("\n", "; ")
                .replace("\r", "")
            )
        else:
            hours = MISSING
        hours = hours if hours else MISSING

        loc = MISSING
        raw_address = MISSING

        if MISSING not in store and country == "CA":
            name = "STORE #" + store

        rec = SgRecord(
            locator_domain=website,
            page_url=loc,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
            raw_address=raw_address,
        )
        sgw.write_row(rec)


def fetch_data(sgw: SgWriter):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [
            executor.submit(fetch_records_global, unum, url, sgw)
            for unum, url in enumerate(searchurls[0:])
        ]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
