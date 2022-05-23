import re
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://maxidespensa.com.hn/ubicaciones-despensa-familiar-honduras"
    domain = "maxidespensa.com.hn/ubicaciones-despensa-familiar-honduras"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="item_ubicacion_link"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="nombre_receta"]/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="cont_ubicacion"]/text()')[-1].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        latitude = re.findall(
            "latitud = '(.+?)';", loc_response.text.replace("\n", "")
        )[0]
        longitude = re.findall(
            "longitud = '(.+?)';", loc_response.text.replace("\n", "")
        )[0]
        city = addr.city
        if city and "Zona" in city:
            city = ""
        if city and city.endswith("."):
            city = city[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="",
            store_number="",
            phone="",
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
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
