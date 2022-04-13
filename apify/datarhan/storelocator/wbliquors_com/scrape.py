from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_usa


def fetch_data():
    session = SgRequests()
    start_url = "https://wbliquors.com/wp-admin/admin-ajax.php"
    domain = "wbliquors.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    frm = {
        "action": "jet_engine_ajax",
        "handler": "get_listing",
        "post_id": "20543",
        "queried_id": "false",
        "element_id": "d9f76d6",
        "page": "1",
        "listing_type": "elementor",
        "isEditMode": "false",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()
    total_pages = data["data"]["filters_data"]["props"]["locationslist"][
        "max_num_pages"
    ]
    for page in range(1, total_pages + 1):
        frm = {
            "action": "jet_engine_ajax",
            "handler": "listing_load_more",
            "query[post_status][]": "publish",
            "query[post_type]": "stores",
            "query[posts_per_page]": "10",
            "query[paged]": "1",
            "query[ignore_sticky_posts]": "1",
            "query[orderby][is-this-a-retailer]": "ASC",
            "query[orderby][city]": "ASC",
            "query[meta_key]": "is-this-a-retailer",
            "query[suppress_filters]": "false",
            "query[jet_smart_filters]": "jet-engine/locationslist",
            "widget_settings[lisitng_id]": "14101",
            "widget_settings[posts_num]": "10",
            "widget_settings[columns]": "1",
            "widget_settings[columns_tablet]": "1",
            "widget_settings[columns_mobile]": "1",
            "widget_settings[is_archive_template]": "",
            "widget_settings[post_status][]": "publish",
            "widget_settings[use_random_posts_num]": "",
            "widget_settings[max_posts_num]": "9",
            "widget_settings[not_found_message]": "No+data+was+found",
            "widget_settings[is_masonry]": "false",
            "widget_settings[equal_columns_height]": "",
            "widget_settings[use_load_more]": "yes",
            "widget_settings[load_more_id]": "",
            "widget_settings[load_more_type]": "scroll",
            "widget_settings[use_custom_post_types]": "",
            "widget_settings[hide_widget_if]": "",
            "widget_settings[carousel_enabled]": "",
            "widget_settings[slides_to_scroll]": "1",
            "widget_settings[arrows]": "true",
            "widget_settings[arrow_icon]": "fa+fa-angle-left",
            "widget_settings[dots]": "",
            "widget_settings[autoplay]": "true",
            "widget_settings[autoplay_speed]": "5000",
            "widget_settings[infinite]": "true",
            "widget_settings[center_mode]": "",
            "widget_settings[effect]": "slide",
            "widget_settings[speed]": "500",
            "widget_settings[inject_alternative_items]": "",
            "widget_settings[scroll_slider_enabled]": "",
            "widget_settings[scroll_slider_on][]": ["desktop", "tablet", "mobile"],
            "widget_settings[custom_query]": "false",
            "widget_settings[custom_query_id]": "",
            "widget_settings[_element_id]": "locationslist",
            "post_id": "false",
            "queried_id": "false",
            "element_id": "false",
            "page": str(page),
            "listing_type": "false",
            "isEditMode": "false",
        }
        data = session.post(start_url, headers=hdr, data=frm).json()
        dom = etree.HTML(data["data"]["html"])

        all_locations = dom.xpath('//div[contains(@class, "jet-listing-grid__item")]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//h5/text()")[0].replace("\n", "").strip()
            raw_addr = poi_html.xpath(
                './/div[@class="elementor-text-editor elementor-clearfix"]/p/text()'
            )[0]
            addr = parse_address_usa(raw_addr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if city and "," in city:
                street_address += " " + city.split(",")[0].strip()
                city = " " + city.split(",")[-1].strip()
            if not city and "," in street_address:
                city = street_address.split(",")[-1].strip()
                street_address = street_address.split(",")[0].strip()
            state = addr.state
            zip_code = addr.postcode
            country_code = addr.country
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/span/text()')
            phone = phone[0] if phone else SgRecord.MISSING
            hoo = poi_html.xpath('.//p[contains(text(), "Monday")]/text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hoo,
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
