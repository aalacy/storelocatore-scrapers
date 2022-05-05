from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    scraped_urls = []
    session = SgRequests()
    start_url = "https://webapi.tedbaker.com/xm/api/regions?locale=es_ES"
    domain = "tedbaker.com"

    data = session.get(start_url).json()
    for e in data["countries"]:
        url = f"https://www.tedbaker.com{e['locales'][0]['url']}"
        if url in scraped_urls:
            continue
        scraped_urls.append(url)
        response = session.get(url)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)
        locator_url = dom.xpath('//a[@title="Find a Store"]/@href')
        locator_url = locator_url[0] if locator_url else ""
        if not locator_url:
            locator_url = dom.xpath(
                '//a[contains(@data-testid, "footer-primary-link")]/@href'
            )[-1]
        locator_url = urljoin(url, locator_url)

        response = session.get(locator_url)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="item store-coord"]')
        for poi_html in all_locations:
            location_name = poi_html.xpath("@data-store-name")[0].replace(",", "")
            raw_address = poi_html.xpath("@data-store-address")[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            state = ""
            zip_code = poi_html.xpath("@data-store-zipcode")[0]
            latitude = poi_html.xpath("@data-store-latitude")[0]
            longitude = poi_html.xpath("@data-store-longitude")[0]
            phone = poi_html.xpath("@data-store-phone")[0].split(":")[-1]
            if "x" in phone:
                phone = ""
            if phone == "/":
                phone = ""
            phone = phone.replace("Tel", "").replace(",", "")
            mon = poi_html.xpath("@data-store-open-monday")[0]
            tue = poi_html.xpath("@data-store-open-tuesday")[0]
            wed = poi_html.xpath("@data-store-open-wed")[0]
            thu = poi_html.xpath("@data-store-open-thursday")[0]
            fri = poi_html.xpath("@data-store-open-friday")[0]
            sat = poi_html.xpath("@data-store-open-sat")[0]
            sun = poi_html.xpath("@data-store-open-sunday")[0]
            hoo = f"Monday: {mon}, Tuesday: {tue}, Wednesday: {wed}, Thursday {thu}, Friday {fri}, Satarday {sat}, Sunday {sun}"
            hoo = " ".join(hoo.split())
            if "/row/" in locator_url:
                country_code = addr.country
            if "/us/" in locator_url:
                country_code = "USA"
            if "/au/" in locator_url:
                country_code = "AU"
            if "/ca/" in locator_url:
                country_code = "CA"
            if "/es/" in locator_url:
                country_code = "ES"
            if "/fr/" in locator_url:
                country_code = "FR"
            if "/de/" in locator_url:
                country_code = "DE"
            if zip_code and country_code == "USA":
                state = zip_code.split()[0]
                zip_code = zip_code.split()[-1]
            if zip_code and country_code == "CA":
                if len(zip_code) > 7:
                    state = zip_code.split()[0]
                    zip_code = " ".join(zip_code.split()[1:])
            if state and len(state) > 2:
                state = state[:2]
            if country_code == "USA" and len(zip_code) > 5:
                zip_code = zip_code[:5]
            if phone and len(phone) < 4:
                phone = ""
            location_type = ""
            booking = poi_html.xpath("@data-url-appointment")
            if booking and "TedBaker" in booking[0]:
                location_type = "TedBaker"
            if "outlet" in location_name.lower():
                location_type = "TedBaker"

            item = SgRecord(
                locator_domain=domain,
                page_url=locator_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
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
