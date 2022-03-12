from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "comfortdental.com"
BASE_URL = "https://comfortdental.com"
LOCATION_URL = "https://comfortdental.com/find-a-dentist/"
API_ENDPOINT = "https://comfortdental.com/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_hoo(page_url):
    location_soup = bs(session.get(page_url, headers=HEADERS).content, "lxml")
    try:
        hours_of_operation = " ".join(
            list(location_soup.find(id="hoursTable").stripped_strings)
        )
    except:
        hours_of_operation = MISSING
    return hours_of_operation


def fetch_data():
    post_headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "Connection": "keep-alive",
    }
    locatornonce = session.post(
        API_ENDPOINT + "?action=locatornonce", headers=HEADERS
    ).json()["nonce"]
    payload = (
        "action=locate&address=Denver%2C+Colorado%2C+Amerika+Serikat&formatted_address=Denver%2C+Colorado%2C+Amerika+Serikat&locatorNonce="
        + locatornonce
        + "&distance=10000000000&latitude=39.7392358&longitude=-104.990251&unit=miles&geolocation=false&allow_empty_address=false"
    )
    json_data = session.post(API_ENDPOINT, headers=post_headers, data=payload).json()
    for data in json_data["results"]:
        location_name = data["title"]
        if "closed" in location_name.lower():
            continue
        page_url = data["permalink"]
        if "aurora-dentist-2" in page_url:
            continue
        soup = bs(data["output"], "lxml")
        soup.find("strong").decompose()
        raw_address = (
            soup.get_text(strip=True, separator="@")
            .replace("@Show on Map", "")
            .replace("@Get Directions", "")
            .split("@")
        )
        del raw_address[0]
        location_soup = bs(session.get(page_url, headers=HEADERS).content, "lxml")
        try:
            hours_of_operation = " ".join(
                list(location_soup.find(id="hoursTable").stripped_strings)
            )
        except:
            hours_of_operation = MISSING
        if "New Braunfels, TX 78130" in raw_address:
            phone = location_soup.find("div", {"id": "phone"}).find("a").text.strip()
        else:
            phone = raw_address[-1]
            del raw_address[-1]
        raw_address = " ".join(raw_address)
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "E Colfax Ave Na Co" in street_address:
            street_address = street_address.replace("Na Co", "").strip()
            city = "Aurora"
            state = "CO"
        if "Coming Soon" in hours_of_operation:
            continue
        phone = phone.rstrip("â€¬")
        store_number = data["id"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        country_code = "US"
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
