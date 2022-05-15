import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://auto.suzuki.es/concesionarios-cercanos"
    domain = "auto.suzuki.es"
    response = session.get("https://auto.suzuki.es/concesionarios#")
    dom = etree.HTML(response.text)
    token = dom.xpath('//meta[@name="csrf-token"]/@content')[0]
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-CSRF-TOKEN": token,
        "X-Requested-With": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.SPAIN], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        frm = {
            "lat_s": lat,
            "lng_s": lng,
            "radio_s": "130",
            "dc_concesionario": "",
            "id_concesionario": "",
        }
        response = session.post(start_url, headers=hdr, data=frm)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath("//li")
        for poi_html in all_locations:
            page_url = re.findall(r'"v11":"(.+?)",', str(etree.tostring(poi_html)))
            page_url = (
                page_url[0] if page_url else "https://auto.suzuki.es/concesionarios#"
            )
            location_name = poi_html.xpath(".//a/span/b/text()")[0]
            raw_address = poi_html.xpath('.//span[@class="search_txt"]/span[1]/text()')
            raw_address = ", ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            phone = poi_html.xpath('.//span[contains(text(), "Teléfono:")]/text()')
            phone = phone[0].split(": ")[-1] if phone else ""
            geo = poi_html.xpath(".//a/@href")[-1].split("_ruta(")[-1].split(",")[:2]
            zip_code = poi_html.xpath('.//span[contains(text(), "C.P.: ")]/text()')[
                0
            ].split(": ")[-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code="ES",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[1],
                longitude=geo[0],
                hours_of_operation="",
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
