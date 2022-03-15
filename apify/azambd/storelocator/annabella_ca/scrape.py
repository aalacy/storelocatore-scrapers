import re
import time
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "annabella.ca"

website = "https://annabella.ca"
MISSING = SgRecord.MISSING


session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}


def request_with_retries(url):
    return session.get(url, headers=headers)


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_stores():
    response = session.get(f"{website}/pages/store-location")
    body = html.fromstring(response.text, "lxml")
    mainDiv = body.xpath('//div[contains(@class, "PageContent")]')[0]

    location_names = mainDiv.xpath('//div[contains(@class, "PageContent")]/h4/text()')
    map_links = mainDiv.xpath('//div[contains(@class, "PageContent")]/p/a/@href')
    p1s = mainDiv.xpath(
        '//div[contains(@class, "PageContent")]/h4/span/text() | //div[contains(@class, "PageContent")]/p/a/text() | //div[contains(@class, "PageContent")]/p/text() | //div[contains(@class, "PageContent")]/p/span/text() | //div[contains(@class, "PageContent")]/div/text()'
    )

    status = ""
    loc_status = []
    allPs = []
    ps = []
    for p in p1s:
        if p == "Map":
            allPs.append(ps)
            ps = []
            loc_status.append(status)
            status = ""
        else:
            if "CLOSED" in p:
                status = p
            elif "relocate" not in p and "OPENING" not in p:
                ps.append(p)
    allPs.append(ps)
    loc_status.append(status)

    stores = []
    count = 0
    for ps in allPs[:-1]:
        location_name = location_names[count].strip()
        status = loc_status[count].strip()
        street_address = ps[0]
        street_address = street_address.replace("\xa0", "")
        if street_address == "":
            street_address = ps[1]
        phone = get_phone(" ".join(ps))

        if len(ps) == 4:
            raw_address = f"{ps[2]} {ps[0]} {ps[1]} {ps[3]}"
            log.info(f"From Length 4: {raw_address}")
            [city, state] = ps[1].split(", ")
            zip_postal = ps[3]

        elif len(ps) == 6:
            raw_address = f"{ps[2]} {ps[3]} {ps[0]} {ps[1]} {ps[4]}"
            log.info(f"From Length 6: {raw_address}")
            if "," in ps[2]:
                [city, state] = ps[2].split(", ")
            else:
                [city, state] = ps[1].split(", ")

            zip_postal = ps[4]

        elif len(ps) == 7:
            raw_address = f"{ps[2]} {ps[3]} {ps[0]} {ps[1]} {ps[4]} {ps[5]}"
            log.info(f"From Length 7: {raw_address}")
            if "," in ps[2]:
                [city, state] = ps[2].split(", ")
            else:
                [city, state] = ps[1].split(", ")

            zip_postal = ps[5]

        else:
            raw_address = f"{ps[2]} {ps[0]} {ps[1]} {ps[3]} {ps[4]}"
            if "," in ps[2]:
                [city, state] = ps[2].split(", ")
            else:
                [city, state] = ps[1].split(", ")

            zip_postal = ps[4]

            if phone == MISSING:
                zip_postal = ps[4]

        location_type = "Clothing Stores"
        if len(status) > 0:
            location_type = status

        stores.append(
            {
                "location_name": location_name.strip(),
                "map_link": map_links[count].strip(),
                "street_address": street_address.strip(),
                "zip_postal": zip_postal.strip(),
                "phone": phone.strip(),
                "city": city.strip(),
                "state": state.strip(),
                "raw_address": raw_address.strip(),
                "location_type": location_type,
            }
        )
        count = count + 1

    return stores


def get_lat_long_array(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if "window.APP_INITIALIZATION_STATE" in script:
            data = (
                script.split("window.APP_INITIALIZATION_STATE=[[[")[-1]
                .rsplit("]", 1)[0]
                .strip()
            )
            return data.split("]")[0].split(",")


def get_lat_long_from_gmap(url):
    log.info(f"Google page: {url}")
    response = session.get(url)
    log.info(f"Google page response: {response}")
    if "goo" in url and response.status_code == 200:
        body = html.fromstring(response.text, "lxml")
        data = get_lat_long_array(body)
        return data[1], data[2]
    else:
        return MISSING, MISSING


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        country_code = "CA"
        location_type = store["location_type"]
        location_name = store["location_name"]
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        phone = store["phone"]

        raw_address = f"{street_address}, {city}, {state} {zip_postal}"
        longitude, latitude = get_lat_long_from_gmap(store["map_link"])
        page_url = f"{website}/pages/store-location"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_type=location_type,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            phone=phone,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
