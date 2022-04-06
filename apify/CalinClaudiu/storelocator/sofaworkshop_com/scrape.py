from lxml import etree
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgscrape.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):
    # Your scraper here
    session = SgRequests()

    start_url = "https://www.sofaworkshop.com/pages/stores"
    domain = "sofaworkshop.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="col-span-4 md:col-span-6 lg:col-span-4 xl:col-span-3 mb-7.5 md:mb-10 xl:mb-15 flex flex-col"]/a/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath("//address/p/text()")[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city.replace(".", "") if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        if "Rm20 1Wn" in street_address:
            zip_code = "Rm20 1Wn"
            street_address = street_address.replace(zip_code, "").strip()
        if "Avon" in street_address:
            city = "Avon"
            street_address = street_address.replace("Avon", "").strip()
        if "Centre" in street_address:
            street_address = street_address.split("Centre")[1].strip()
        country_code = "GB"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="contact mb-10 md:mb-0"]/p/text()')[-1]
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        base = BeautifulSoup(loc_response.text, "lxml")
        hours_of_operation = " ".join(
            list(base.find(class_="opening-hours").dl.stripped_strings)
        )

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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
