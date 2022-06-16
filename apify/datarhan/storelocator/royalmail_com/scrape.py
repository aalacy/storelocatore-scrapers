from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries
from sglogging import sglog


def fetch_data():
    session = SgRequests(proxy_country="gb")
    scraped_urls = []
    start_url = "https://www.royalmail.com/capi/rml/bf/v1/locations/branchFinder?postCode={}&latitude={}&longitude={}&searchRadius=40&count=5&selectedName=&officeType=&type=undefined&appliedFilters=undefined"
    domain = "royalmail.com"
    log = sglog.SgLogSetup().get_logger(logger_name=domain)
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    codes = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=40
    )
    for zipcode, coord in codes:
        url = start_url.format(zipcode, coord[0], coord[1])
        all_locations = session.get(url, headers=hdr)
        if all_locations.status_code != 200:
            log.info(f"Status Code: {all_locations.status_code} for {zipcode}")
            continue
        for poi in all_locations.json():
            location_name = poi["officeDetails"]["name"]
            raw_address = poi["officeDetails"]["address1"]
            if poi["officeDetails"]["address2"]:
                raw_address += " " + poi["officeDetails"]["address2"]
            if poi["officeDetails"]["address3"]:
                raw_address += " " + poi["officeDetails"]["address3"]
            if poi["officeDetails"]["address4"]:
                raw_address += " " + poi["officeDetails"]["address4"]
            if poi["officeDetails"]["address5"]:
                raw_address += " " + poi["officeDetails"]["address5"]
            addr = parse_address_intl(raw_address)
            city = addr.city
            street_address = addr.street_address_1
            if street_address and addr.street_address_2:
                street_address += " " + addr.street_address_2
            else:
                street_address = addr.street_address_2
            hoo = ""
            location_type = poi["type"]
            page_url = ""
            phone = ""
            if location_type == "PO":
                page_url = f'https://www.royalmail.com/services-near-you/post-office/{location_name.lower().replace(" ", "-")}-{poi["officeDetails"]["postcode"].lower().replace(" ", "-")}'
            if location_type == "DO":
                page_url = f'https://www.royalmail.com/services-near-you/delivery-office/{location_name.lower().replace(" ", "-")}-{poi["officeDetails"]["postcode"].lower().replace(" ", "-")}'
            if page_url:
                if page_url in scraped_urls:
                    continue
                scraped_urls.append(page_url)
                loc_response = session.get(page_url, headers=hdr)
                loc_dom = etree.HTML(loc_response.text)
                phone = loc_dom.xpath('//div[@class="phone-number"]/a/text()')
                phone = phone[0].strip() if phone else ""
                hoo = loc_dom.xpath('//div[@class="opening-hours-wrapper"]/div//text()')
                hoo = (
                    " ".join([e.strip() for e in hoo if e.strip()])
                    .split(" opening hours.")[-1]
                    .split("Please check")[0]
                    .strip()
                    .split("have changed ")[-1]
                )
                raw_address = loc_dom.xpath('//div[@class="branch-address"]/text()')[0]
                addr = parse_address_intl(raw_address)
                city = addr.city
                street_address = addr.street_address_1
                if street_address and addr.street_address_2:
                    street_address += " " + addr.street_address_2
                else:
                    street_address = addr.street_address_2
            hoo = hoo.replace("Our opening hours have changed ", "")
            if city:
                city = city.replace(" Ze2", "")
            if not street_address:
                street_address = location_name

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=poi["officeDetails"]["county"],
                zip_postal=poi["officeDetails"]["postcode"],
                country_code="",
                store_number="",
                phone=phone,
                location_type=poi["type"],
                latitude=poi["locationDetails"]["latitude"],
                longitude=poi["locationDetails"]["longitude"],
                hours_of_operation=hoo,
                raw_address=raw_address,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
