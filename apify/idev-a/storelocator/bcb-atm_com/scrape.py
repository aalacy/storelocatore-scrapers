from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bcb-atm")


_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://bcb-atm.com",
    "referer": "https://bcb-atm.com/bitcoin-atm-map/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bcb-atm.com"
base_url = "https://bcb-atm.com/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            data = {
                "post__not_in[]": "3925",
                "action": "wiloke_loadmore_listing_layout",
                "posts_per_page": "100",
                "listing_locations": "",
                "latLng": "",
                "listing_cats": "",
                "get_posts_from": "",
                "is_focus_query": "false",
                "is_open_now": "false",
                "is_highest_rated": "false",
                "paged": str(page),
                "customerUTCTimezone": "UTC--7",
                "s": "",
                "displayStyle": "loadmore",
                "sUnit": "mi",
                "sWithin": "50",
                "atts[layout]": "circle-thumbnail",
                "atts[get_posts_from]": "the_both_listing_location_and_listing_cat",
                "atts[listing_cat]": "",
                "atts[listing_location]": "",
                "atts[listing_tag]": "",
                "atts[include]": "",
                "atts[show_terms]": "listing_location",
                "atts[filter_type]": "none",
                "atts[btn_name]": "Load More",
                "atts[viewmore_page_link]": "#",
                "atts[btn_position]": "text-center",
                "atts[order_by]": "post_date",
                "atts[order]": "DESC",
                "atts[display_style]": "loadmore",
                "atts[btn_style]": "listgo-btn--default",
                "atts[btn_size]": "listgo-btn--small",
                "atts[posts_per_page]": "6",
                "atts[image_size]": "large",
                "atts[toggle_render_favorite]": "enable",
                "atts[favorite_description]": "Save",
                "atts[toggle_render_view_detail]": "enable",
                "atts[view_detail_text]": "",
                "atts[toggle_render_find_direction]": "enable",
                "atts[find_direction_text]": "",
                "atts[toggle_render_link_to_map_page]": "enable",
                "atts[link_to_map_page_text]": "",
                "atts[toggle_render_post_excerpt]": "enable",
                "atts[toggle_render_address]": "enable",
                "atts[toggle_render_author]": "enable",
                "atts[toggle_render_rating]": "enable",
                "atts[limit_character]": "6",
                "atts[filter_result_description]": "*open_result* %found_listing% %result_text=Result|Results% *end_result* in %total_listing% Destinations",
                "atts[block_id]": "",
                "atts[css]": "",
                "atts[map_page]": "",
                "atts[term_ids]": "",
                "atts[post_authors]": "",
                "atts[created_at]": "",
                "atts[extract_class]": "",
                "atts[location_latitude_longitude]": "",
                "atts[s_within_radius]": "6",
                "atts[s_unit]": "mi",
                "atts[isTax]": "false",
                "atts[sidebar]": "right",
                "atts[wrapper_class]": "listings circle-thumbnail",
                "atts[item_class]": "listing circle-thumbnail",
                "atts[before_item_class]": "col-sm-12 col-md-12",
                "currentPageID": "495",
            }
            res = session.post(base_url, headers=_headers, data=data).json()
            if not res.get("success"):
                break
            soup = bs(res["data"]["content"], "lxml")
            locations = soup.select("div.col-sm-12.col-md-12")
            if not locations:
                break
            page += 1
            for _ in locations:
                page_url = _.select_one("h3 a")["href"]
                logger.info(page_url)
                sp1 = bs(session.post(page_url, headers=_headers).text, "lxml")
                raw_address = sp1.select_one("div.wil_accordion__content").text.strip()
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                try:
                    coord = (
                        _.select_one("div.tb__cell.listgo-redirect-to-btn a")["href"]
                        .split("/")[-1]
                        .split(",")
                    )
                except:
                    coord = ["", ""]
                phone = ""
                if _.select_one("span.address-phone_number a"):
                    phone = _.select_one("span.address-phone_number a").text.strip()

                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("div.widget_author-calendar li")
                ]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one("h3.listing__title").text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="UK",
                    latitude=coord[0],
                    longitude=coord[1].replace("%20", ""),
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
