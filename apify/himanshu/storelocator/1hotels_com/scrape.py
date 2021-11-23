import re
import json
from lxml import etree
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "1hotels_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://1hotels.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    start_url = "https://www.1hotels.com/about-us/contact-us"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//a[img]/@href")[1:]
    for url in all_locations:
        if domain not in url:
            continue
        page_url = url.replace("/contact-us", "")
        loc_response = session.get(page_url)
        log.info(page_url)

        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
        if poi:
            poi = json.loads(poi[0])
            poi = poi["@graph"][0]

            location_name = poi["name"]
            try:
                street_address = poi["contactPoint"]["areaServed"]["address"][
                    "streetAddress"
                ]
                city = poi["contactPoint"]["areaServed"]["address"]["addressLocality"]
                state = poi["contactPoint"]["areaServed"]["address"]["addressRegion"]
                zip_postal = poi["contactPoint"]["areaServed"]["address"]["postalCode"]
                country_code = poi["contactPoint"]["areaServed"]["address"][
                    "addressCountry"
                ]

            except:
                address = poi["address"]
                street_address = address["streetAddress"]
                city = address["addressLocality"]
                state = address["addressRegion"]
                zip_postal = address["postalCode"]
                country_code = address["addressCountry"]
            try:
                phone = poi["contactPoint"]["telephone"]
            except:
                phone = MISSING
            store_number = MISSING

            location_type = poi["@type"]
            geo = re.findall('location":{(.+),"lat_sin', loc_response.text)[0]
            geo = json.loads("{" + geo + "}")
            latitude = geo["lat"]
            longitude = geo["lng"]
        else:
            location_name = loc_dom.xpath(
                '//p[@class="directions__address"]/a//text()'
            )[0].strip()
            raw_address = loc_dom.xpath('//p[@class="directions__address"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = MISSING
            zip_postal = raw_address[1].split(", ")[-1].split()[-1]
            country_code = MISSING
            store_number = MISSING
            phone = loc_dom.xpath(
                '//a[strong[contains(text(), "Reservations")]]/text()'
            )[0].strip()
            location_type = MISSING
            geo = re.findall('location":{(.+),"lat_sin', loc_response.text)[0]
            geo = json.loads("{" + geo + "}")
            latitude = geo["lat"]
            longitude = geo["lng"]
        hours_of_operation = MISSING
        phone = phone.replace("=", "")
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
