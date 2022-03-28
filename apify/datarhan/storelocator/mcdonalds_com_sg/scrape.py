from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = (
        "https://www.mcdonalds.com.sg/locate-us?ajax_form=1&_wrapper_format=drupal_ajax"
    )
    domain = "mcdonalds.com.sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "search_query": "singapore",
        "form_build_id": "form-JW36V3wo4_TMTDfnll_tKUQIb0OUrqap11-TLDRw_KA",
        "form_id": "mcdonalds_gmap_form",
        "_triggering_element_name": "op",
        "_triggering_element_value": "Search Location",
        "_drupal_ajax": "1",
        "ajax_page_state[theme]": "mcdonalds",
        "ajax_page_state[theme_token]": "",
        "ajax_page_state[libraries]": "core/drupal.ajax,core/jquery.form,mcdonalds/base,mcdonalds/icomoon,mcdonalds_location/filter,mcdonalds_location/mcdgoogle-map-apis,system/base",
    }
    data = session.post(start_url, data=frm, headers=hdr).json()
    dom = etree.HTML(data[-1]["data"])
    all_coords = data[2]["args"][0]

    all_locations = dom.xpath('//div[contains(@id, "location")]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="info"]/strong/text()')[0]
        raw_address = poi_html.xpath('.//div[@class="location-address"]//text()')
        raw_address_raw = [e.strip() for e in raw_address if e.strip()]
        raw_address = ", ".join(raw_address_raw)
        addr = parse_address_intl(raw_address)
        if len(raw_address_raw) == 2:
            street_address = raw_address_raw[0]
        else:
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
        phone = poi_html.xpath(
            './/div[@class="location-contact"]/div[@class="value"]/text()'
        )
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath(
            './/div[@class="location-ophour"]/div[@class="value"]/p[1]//text()'
        )
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .split("McCaf")[0]
            .replace("Main Store: ", "")
            .strip()
        )
        store_id = int(poi_html.xpath("@data-attr")[0])
        latitude = [e[0] for e in all_coords if e[2] == store_id][0]
        longitude = [e[1] for e in all_coords if e[2] == store_id][0]
        city = addr.city
        zip_code = addr.postcode
        if not city and len(raw_address_raw) == 2:
            city = raw_address_raw[-1].split()[0]
            zip_code = raw_address_raw[-1].split()[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.mcdonalds.com.sg/locate-us/",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="SG",
            store_number="",
            phone=phone,
            location_type="",
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
