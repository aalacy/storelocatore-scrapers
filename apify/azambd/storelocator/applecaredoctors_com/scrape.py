import re
from lxml import etree

from sgpostal.sgpostal import parse_address_usa

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

MISSING = "<MISSING>"
session = SgRequests()

log = sglog.SgLogSetup().get_logger(logger_name="applecareurgentcare.com")


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            country_code = data.country

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country_code is None or len(country_code) == 0:
                country_code = MISSING

            return street_address, city, state, zip_postal, country_code
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def fetch_data():
    start_url = "https://applecareurgentcare.com/urgent-care-locations/"
    domain = "applecareurgentcare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    log.info(f"{start_url} Response: {response}")
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class=" main-menu-link main-menu-link-sub"]/@href')
    log.info("Listing Page URLs...")
    for store_url in all_locations:
        if "urgent-care-locations" in str(store_url):
            log.info(f"Crawling: {store_url}")
            loc_response = session.get(store_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//h3[@itemprop="headline"]/text()')
            location_name = location_name[0] if location_name else MISSING
            raw_address = loc_dom.xpath(
                '//h3[contains(text(), "Address")]/following-sibling::h3[1]/text()'
            )
            raw_address = ", ".join([e.strip() for e in raw_address]).replace(
                "\r\n", ", "
            )
            log.info(f"Raw Address: {raw_address}")
            street_address, city, state, zip_postal, country_code = get_address(
                raw_address
            )

            store_number = MISSING
            phone = loc_dom.xpath('//h3[contains(text(), "Ph.:")]/text()')
            phone = phone[0].split(": ")[-1] if phone else MISSING
            location_type = MISSING
            try:
                geolink = loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                try:
                    geo = re.findall(r"[0-9]{2}\.[0-9]+,[0-9]{1,3}\.[0-9]+", geolink)[
                        0
                    ].split(",")
                except:
                    geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{1,3}\.[0-9]+", geolink)[
                        0
                    ].split(",")

                if len(geo) == 2:
                    latitude = geo[0]
                    longitude = geo[1]
                else:
                    latitude = MISSING
                    longitude = MISSING
            except:
                latitude = MISSING
                longitude = MISSING

            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Hours")]/following-sibling::div//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
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

            yield item


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
