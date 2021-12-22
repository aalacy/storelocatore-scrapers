from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="us")
    start_url = "https://lubengoautocare.com/locations-region/"
    domain = "lubengoautocare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="the_list_item_action"]/a/@href')[1:]
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath(
            '//h3[@class="the_list_item_headline hds_color"]/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        location_name = (
            loc_dom.xpath('//meta[@property="og:title"]/@content')[0]
            .split("|")[0]
            .strip()
        )
        city = addr.city
        street_address = raw_address.split(city)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = (
            loc_dom.xpath('//h3[contains(text(), "Phone Number:")]/text()')[0]
            .split(":")[-1]
            .strip()
        )
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2")[0]
            .split("!3d")
        )
        latitude = geo[-1].split("!")[0]
        longitude = geo[0]
        hoo = loc_dom.xpath('//p[b[contains(text(), "Hours")]]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            "Monday " + " ".join(hoo).split("Monday ")[-1] if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
