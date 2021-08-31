import json
import re

from lxml import etree

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.1hotels.com/about-us/contact-us"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//a[img]/@href")[1:]
    for url in all_locations:
        if domain not in url:
            continue
        store_url = url.replace("/contact-us", "")

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
        if poi:
            poi = json.loads(poi[0])
            poi = poi["@graph"][0]

            location_name = poi["name"]
            street_address = poi["contactPoint"]["areaServed"]["address"][
                "streetAddress"
            ]
            city = poi["contactPoint"]["areaServed"]["address"]["addressLocality"]
            state = poi["contactPoint"]["areaServed"]["address"]["addressRegion"]
            zip_code = poi["contactPoint"]["areaServed"]["address"]["postalCode"]
            country_code = poi["contactPoint"]["areaServed"]["address"][
                "addressCountry"
            ]
            store_number = "<MISSING>"
            phone = poi["contactPoint"]["telephone"]
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
            state = "<MISSING>"
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//a[strong[contains(text(), "Reservations")]]/text()'
            )[0].strip()
            location_type = "<MISSING>"
            geo = re.findall('location":{(.+),"lat_sin', loc_response.text)[0]
            geo = json.loads("{" + geo + "}")
            latitude = geo["lat"]
            longitude = geo["lng"]
        hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
