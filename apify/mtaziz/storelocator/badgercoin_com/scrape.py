from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import re


logger = SgLogSetup().get_logger("badgercoin_com")
MISSING = SgRecord.MISSING
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


def clean_daytime(daytime):
    time_pattern = r"\"\w+.\w+.?\w+.\w+"
    daytime = re.findall(time_pattern, daytime)
    daytime = [i.strip('"') for i in daytime]
    daytime = ": ".join(daytime)
    return daytime


def get_hoo(app_options):
    hours = app_options.split("tel:")[-1]
    hours = re.findall(r"Sunday(.*)Sunday", hours)
    hours = '"Sunday' + "".join(hours)
    hours = hours.split("]]]]")
    hours = [clean_daytime(i) for i in hours]
    hours = [i for i in hours if i]
    return hours


def fetch_records(http: SgRequests):
    gurls = get_googlemap_based_store_urls()
    for idx, gurl in enumerate(gurls[0:]):
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
        add = meta_add_data.split("·")[1].strip()
        pai = parse_address_intl(add)
        sa = pai.street_address_1
        street_address = sa if sa else MISSING
        logger.info(f"[{idx}] st_add: {street_address}")

        city = pai.city
        city = city if city else MISSING
        logger.info(f"[{idx}] city: {city}")

        state = pai.state
        state = state if state else MISSING
        logger.info(f"[{idx}] state: {state}")

        zip_postal = pai.postcode
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"[{idx}] zip: {zip_postal}")

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
        hoo = get_hoo(app_options)
        hours_of_operation = "; ".join(hoo) if hoo else MISSING
        logger.info(f"[{idx}] HOO: {hours_of_operation}")

        raw_address = add or MISSING

        yield SgRecord(
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
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
