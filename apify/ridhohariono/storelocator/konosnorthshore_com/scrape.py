from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "konosnorthshore.com"
BASE_URL = "https://www.konosnorthshore.com"
LOCATION_URL = "https://www.konosnorthshore.com/"
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


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def get_hoo(data):
    hoo = MISSING
    for i in range(len(data)):
        if re.search(r"Monday|Sunday|Open Everyday", data[i]):
            hoo = data[i] + ": " + data[i + 1].replace("Hours:", "").strip()
            break
    return hoo


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    out_tag = bs(
        """<section class="widget clearfix widget_text">
            <h3 class="widgettitle">Longford Shoppes At Summerlin Parkway</h3>
            <div class="textwidget">
                <p>7591 W. Washington Ave<br>LV, 89128</p>
                <p><a href="tel:1-808-637-9211">(702) 331-1824</a></p>
                <p><strong>Monday – Sunday</strong><br><strong> Hours: 7:00am – 8:00pm</strong> </p>
            </div>
        </section>""",
        "lxml",
    )
    soup.body.insert(1, out_tag)
    element = soup.find_all("section", {"class": "widget clearfix widget_text"})
    del element[2]
    for row in element[:-1]:
        info = row.get_text(strip=True, separator="@").split("@")
        location_name = info[0]
        raw_address = ""
        phone = MISSING
        for addr in info[:-1]:
            if "808" in addr or "702" in addr:
                phone = addr
                break
            raw_address += " " + addr
        street_address, city, state, zip_postal = getAddress(raw_address.strip())
        if "Lv" in street_address:
            street_address = street_address.replace("Lv", "")
            city = "Las Vegas"
            state = "Nevada"
        hours_of_operation = get_hoo(info)
        country_code = "US"
        store_number = MISSING
        location_type = "konosnorthshore"
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
