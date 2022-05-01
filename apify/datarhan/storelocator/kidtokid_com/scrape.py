from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kidtokid.com"
    start_url = "https://kidtokid.com/stores/"
    for p in range(0, 11):
        frm = {
            "action": "jet_engine_ajax",
            "handler": "listing_load_more",
            "query[post_status]": "publish",
            "query[post_type]": "location",
            "query[posts_per_page]": "50",
            "query[paged]": "1",
            "query[ignore_sticky_posts]": "1",
            "query[order]": "ASC",
            "query[orderby]": "name",
            "query[post__not_in][]": "3873",
            "query[suppress_filters]": "false",
            "query[jet_smart_filters]": "jet-engine/usQuery",
            "widget_settings[lisitng_id]": "1035",
            "widget_settings[posts_num]": "50",
            "widget_settings[columns]": "1",
            "widget_settings[columns_tablet]": "1",
            "widget_settings[columns_mobile]": "1",
            "widget_settings[is_archive_template]": "",
            "widget_settings[post_status][]": "publish",
            "widget_settings[use_random_posts_num]": "",
            "widget_settings[max_posts_num]": "50",
            "widget_settings[not_found_message]": "No stores were found",
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
            "widget_settings[arrow_icon]": "fa fa-angle-left",
            "widget_settings[dots]": "",
            "widget_settings[autoplay]": "true",
            "widget_settings[autoplay_speed]": "5000",
            "widget_settings[infinite]": "true",
            "widget_settings[center_mode]": "",
            "widget_settings[effect]": "slide",
            "widget_settings[speed]": "500",
            "widget_settings[inject_alternative_items]": "",
            "widget_settings[scroll_slider_enabled]": "",
            "widget_settings[custom_query]": "false",
            "widget_settings[custom_query_id]": "",
            "widget_settings[_element_id]": "usQuery",
            "page_settings[post_id]": "false",
            "page_settings[queried_id]": "false",
            "page_settings[element_id]": "false",
            "page_settings[page]": str(p),
            "listing_type": "false",
            "isEditMode": "false",
            "iwcUZYQabyzD": "ecC[sv",
            "odWjEFpswhQ": "HJ[X1U",
        }

        hdr = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        response = session.post(start_url, data=frm, headers=hdr)
        if response.status_code != 200:
            continue
        data = response.json()
        dom = etree.HTML(data["data"]["html"])
        if dom is None:
            continue
        all_locations = dom.xpath('//a[contains(@href, "/location/")]/@href')
        for url in list(set(all_locations)):
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = " ".join(
                loc_dom.xpath(
                    '//div[@class="elementor-column-wrap elementor-element-populated"]//h1/text()'
                )
            )
            raw_address = loc_dom.xpath(
                '//div[div[h2[contains(text(), "Contact Us")]]]/following-sibling::div//p/text()'
            )
            if not raw_address:
                continue
            country_code = "US"
            zip_code = " ".join(raw_address[1].split(", ")[-1].split()[1:])
            if len(zip_code.split()) == 2:
                country_code = "CA"
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/span/text()')
            phone = phone[0] if phone else ""
            hoo = loc_dom.xpath(
                '//div[div[h2[contains(text(), "Store Hours")]]]/following-sibling::div//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1].split()[0],
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
