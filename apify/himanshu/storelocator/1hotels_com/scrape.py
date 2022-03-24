import re
import json
from lxml import etree
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
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
    all_locations = dom.xpath("//header/a/@href")
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
            if "Sprouting Fall 2022" in location_name:
                continue
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
            raw_address = (
                street_address
                + " "
                + city
                + " "
                + state
                + " "
                + zip_postal
                + " "
                + country_code
            )
        else:
            loc_dom = BeautifulSoup(loc_response.text, "html.parser")
            location_name = loc_dom.find("h1").text
            raw_address = (
                loc_dom.find(
                    "div",
                    {"class": "caption col-md-10 ml-auto mr-auto text-lg-center card"},
                )
                .find("p")
                .text
            )
            phone = loc_response.text.split('<a href="tel:')[1].split('"')[0]
            if "Planning an upcoming trip" in raw_address:
                raw_address = (
                    loc_dom.find("p", {"class": "directions__address"})
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
                location_name = raw_address[0]
                raw_address = " ".join(raw_address[1:])
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = pa.country
            country_code = country_code.strip() if country_code else MISSING

            store_number = MISSING

            location_type = MISSING
        try:
            longitude, latitude = (
                loc_response.text.split('"coordinates":"[')[1].split("]")[0].split(",")
            )
        except:
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
            raw_address=raw_address,
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
