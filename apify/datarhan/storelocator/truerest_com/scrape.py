from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://truerest.com/wp-admin/admin-ajax.php"
    domain = "truerest.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=400
    )
    for lat, lng in all_coords:
        frm = {
            "action": "get_stores",
            "lat": lat,
            "lng": lng,
            "radius": "400",
            "categories[0]": "",
        }
        all_locations = session.post(start_url, headers=hdr, data=frm).json()
        for i, poi in all_locations.items():
            if poi["ca"]["0"] == "Coming Soon":
                continue
            page_url = poi["we"].strip()
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)
            if loc_dom.xpath('//h4[contains(text(), "Coming Soon!")]'):
                continue
            if loc_dom.xpath('//h4[contains(text(), "Opening February")]'):
                continue

            poi_html = etree.HTML(poi["de"])
            raw_address = poi_html.xpath('//p[@class="locations_info"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            if len(raw_address) == 1:
                raw_address.append(
                    poi_html.xpath(
                        '//p[@class="locations_info"]/following-sibling::p[1]/text()'
                    )[0]
                )
            addr = parse_address_intl(" ".join(raw_address))
            phone = poi_html.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            hoo = loc_dom.xpath('//table[@class="mabel-bhi-businesshours"]//text()')
            hoo = " ".join(hoo)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["na"],
                street_address=raw_address[0],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                store_number=poi["ID"],
                phone=phone,
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=hoo,
                raw_address=" ".join(raw_address),
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
