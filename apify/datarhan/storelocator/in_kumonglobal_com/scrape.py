import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://{}.kumonglobal.com/wp-admin/admin-ajax.php"
    domain = "in.kumonglobal.com"
    hdr = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    frm_my = {
        "store_locatore_search_input": "Kuala Lumpur Kuala Lumpur, Malaysia",
        "store_locatore_search_lat": "3.139003",
        "store_locatore_search_lng": "101.686855",
        "store_locatore_search_radius": "2000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "3.139003",
        "lng": "101.686855",
    }
    frm_in = {
        "store_locatore_search_input": "New Delhi, India , India",
        "store_locatore_search_lat": "28.6139391",
        "store_locatore_search_lng": "77.2090212",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "28.6139391",
        "lng": "77.2090212",
    }

    frm_bn = {
        "store_locatore_search_input": "Brunei brunei, Brunei Darussalam",
        "store_locatore_search_lat": "4.535277",
        "store_locatore_search_lng": "114.727669",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "4.535277",
        "lng": "114.727669",
    }

    frm_kh = {
        "store_locatore_search_input": "Sangkat Tumnob Teuk, Khan Chamkarmon, Phnom Penh Phnom Penh, Cambodia",
        "store_locatore_search_lat": "11.5510525",
        "store_locatore_search_lng": "104.9273392",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "11.5510525",
        "lng": "104.9273392",
    }

    frm_id = {
        "store_locatore_search_input": "ln. Ahmad Yani No. 37 Utan Kayu Selatan Jakarta INDONESIA Jakarta, Indonesia",
        "store_locatore_search_lat": "-6.2009301",
        "store_locatore_search_lng": "106.8730712",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "-6.2009301",
        "lng": "106.8730712",
    }

    frm_ph = {
        "store_locatore_search_input": "19th Floor Philamlife Tower, 8767 Paseo de Roxas, Makati,, 1226 Metro Manila, Philippines Metro Manila, Philippines",
        "store_locatore_search_lat": "14.5572638",
        "store_locatore_search_lng": "121.021859",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "14.5572638",
        "lng": "121.021859",
    }

    frm_sg = {
        "store_locatore_search_input": "Singapore, Singapore",
        "store_locatore_search_lat": "1.352083",
        "store_locatore_search_lng": "103.819836",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "1.352083",
        "lng": "103.819836",
    }

    frm_th = {
        "store_locatore_search_input": "Thailand , Thailand",
        "store_locatore_search_lat": "15.870032",
        "store_locatore_search_lng": "100.992541",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "15.870032",
        "lng": "100.992541",
    }

    frm_vn = {
        "store_locatore_search_input": "Ho Chi Minh, Viet Nam",
        "store_locatore_search_lat": "10.8230989",
        "store_locatore_search_lng": "106.6296638",
        "store_locatore_search_radius": "20000",
        "store_locator_category": "",
        "action": "make_search_request",
        "lat": "10.8230989",
        "lng": "106.6296638",
    }
    countries = {
        "in": frm_in,
        "bn": frm_bn,
        "kh": frm_kh,
        "id": frm_id,
        "ph": frm_ph,
        "sg": frm_sg,
        "th": frm_th,
        "vn": frm_vn,
        "my": frm_my,
    }
    for c, frm in countries.items():
        response = session.post(start_url.format(c), headers=hdr, data=frm)
        dom = etree.HTML(response.text)
        data = (
            dom.xpath('//script[contains(text(), "locations")]/text()')[0]
            .split("locations =")[-1]
            .split(";\n        store_locator")[0]
        )
        data = json.loads(data)

        for poi in data["locations"]:
            poi_html = etree.HTML(poi["infowindow"])
            page_url = poi_html.xpath("//a/@href")[0]

            location_name = poi_html.xpath("//a/text()")[0]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//li[span[contains(text(), "Address: ")]]/text()'
            )[-1].strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            phone = (
                loc_dom.xpath('//li[span[contains(text(), "Phone: ")]]/text()')[-1]
                .strip()
                .split("/")[0]
                .split(",")[0]
            )
            hoo = loc_dom.xpath(
                '//li[span[strong[contains(text(), "Schedule")]]]//text()'
            )
            if not hoo:
                hoo = loc_dom.xpath('//li[strong[contains(text(), "Schedule")]]/text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)
            if "Schedule" in hoo:
                if "Schedule:" in hoo:
                    hoo = hoo.split("Parent")[0].replace("Kasthuri", "")
                else:
                    hoo = hoo.split("Schedule")[1]
            if "Schedule " in hoo:
                hoo = hoo.split("Schedule ")[1]
            hoo = (
                hoo.split("Parent Orientation")[0]
                .split(".com ")[-1]
                .split("*")[0]
                .strip()
            )
            if "Please contact the center for more details" in hoo:
                hoo = ""
            if not hoo:
                hoo = loc_dom.xpath(
                    '//div[@class="store_locator_content"]/ul/li[4]/text()'
                )
                hoo = " ".join([e.strip() for e in hoo])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=c,
                store_number="",
                phone=phone,
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=hoo,
                raw_address=raw_address,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
