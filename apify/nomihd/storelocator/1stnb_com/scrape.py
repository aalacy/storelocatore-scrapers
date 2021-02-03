# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from bs4 import BeautifulSoup as BS
import json

website = "1stnb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []
    session = SgRequests()
    stores_req = session.get("https://www.1stnb.com/locator")
    status = "Please solve this CAPTCHA to request unblock to the website"
    if status in stores_req.text:
        while status in stores_req.text:
            try:
                log.info("Retrying due to CAPTCHA")
                session = SgRequests()
                stores_req = session.get("https://www.1stnb.com/locator")
            except:
                pass

    count = 0
    while True:
        if count == 0:
            theme_token = (
                stores_req.text.split('"theme_token":"')[1]
                .strip()
                .split('",')[0]
                .strip()
            )
            view_dom_id = (
                stores_req.text.split('"view_dom_id":"')[1]
                .strip()
                .split('",')[0]
                .strip()
            )

        else:
            theme_token = (
                stores_req.text.split('"theme_token":"')[1]
                .strip()
                .split('",')[0]
                .strip()
            )
            view_dom_id = (
                stores_req.text.split('"view_dom_id":"')[1]
                .strip()
                .split('",')[0]
                .strip()
            )

        data = [
            ("view_name", "Locator"),
            ("view_display_id", "page"),
            ("view_args", ""),
            ("view_path", "locator"),
            ("view_base_path", "locator"),
            ("pager_element", "0"),
            ("field_locator_type_tid[0]", "21"),
            ("field_state_tid", "All"),
            ("ajax_html_ids[]", "skip-link"),
            ("ajax_html_ids[]", "page"),
            ("ajax_html_ids[]", "Top"),
            ("ajax_html_ids[]", "header-wrapper"),
            ("ajax_html_ids[]", "header"),
            ("ajax_html_ids[]", "logo"),
            ("ajax_html_ids[]", "search-block-form"),
            ("ajax_html_ids[]", "edit-search-block-form--2"),
            ("ajax_html_ids[]", "edit-actions"),
            ("ajax_html_ids[]", "edit-submit"),
            ("ajax_html_ids[]", "menu-bar-wrapper"),
            ("ajax_html_ids[]", "block-tb-megamenu-main-menu"),
            ("ajax_html_ids[]", "tb-megamenu-column-1"),
            ("ajax_html_ids[]", "tb-megamenu-column-2"),
            ("ajax_html_ids[]", "tb-megamenu-column-3"),
            ("ajax_html_ids[]", "tb-megamenu-column-7"),
            ("ajax_html_ids[]", "tb-megamenu-column-4"),
            ("ajax_html_ids[]", "tb-megamenu-column-5"),
            ("ajax_html_ids[]", "tb-megamenu-column-6"),
            ("ajax_html_ids[]", "tb-megamenu-column-13"),
            ("ajax_html_ids[]", "tb-megamenu-column-9"),
            ("ajax_html_ids[]", "tb-megamenu-column-8"),
            ("ajax_html_ids[]", "tb-megamenu-column-10"),
            ("ajax_html_ids[]", "tb-megamenu-column-11"),
            ("ajax_html_ids[]", "tb-megamenu-column-12"),
            ("ajax_html_ids[]", "main-wrapper"),
            ("ajax_html_ids[]", "page-title"),
            ("ajax_html_ids[]", "breadcrumb-wrapper"),
            ("ajax_html_ids[]", "main-content"),
            ("ajax_html_ids[]", "block-system-main"),
            ("ajax_html_ids[]", "views-exposed-form-Locator-page"),
            ("ajax_html_ids[]", "edit-field-locator-type-tid--9-wrapper"),
            ("ajax_html_ids[]", "edit-field-locator-type-tid--9"),
            ("ajax_html_ids[]", "edit-field-city-value--9-wrapper"),
            ("ajax_html_ids[]", "edit-field-city-value--9"),
            ("ajax_html_ids[]", "edit-field-state-tid--9-wrapper"),
            ("ajax_html_ids[]", "edit-field-state-tid--9"),
            ("ajax_html_ids[]", "edit-field-zip-code-value--9-wrapper"),
            ("ajax_html_ids[]", "edit-field-zip-code-value--9"),
            ("ajax_html_ids[]", "edit-submit-locator--9"),
            ("ajax_html_ids[]", "sidebar-first-wrapper"),
            ("ajax_html_ids[]", "block-menu-menu-side-menu--2"),
            ("ajax_html_ids[]", "block-quicktabs-qucktabs--2"),
            ("ajax_html_ids[]", "quickset-qucktabs"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-header-0"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-panel-0"),
            ("ajax_html_ids[]", "block-views-latest-article-block--2"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-header-1"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-panel-1"),
            ("ajax_html_ids[]", "block-menu-menu-fraud-prevention-center--2"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-header-2"),
            ("ajax_html_ids[]", "ui-accordion-quickset-qucktabs-panel-2"),
            ("ajax_html_ids[]", "block-views-popular-block--2"),
            ("ajax_html_ids[]", "block-block-1--2"),
            ("ajax_html_ids[]", "footer-wrapper"),
            ("ajax_html_ids[]", "footer"),
            ("ajax_html_ids[]", "social-share-wrapper"),
            ("ajax_page_state[theme]", "tb_fnbt"),
            ("ajax_page_state[css][modules/system/system.base.css]", "1"),
            ("ajax_page_state[css][modules/system/system.menus.css]", "1"),
            ("ajax_page_state[css][modules/system/system.messages.css]", "1"),
            ("ajax_page_state[css][modules/system/system.theme.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/nucleus/nucleus/css/base.css]",
                "1",
            ),
            ("ajax_page_state[css][misc/ui/jquery.ui.core.css]", "1"),
            ("ajax_page_state[css][misc/ui/jquery.ui.theme.css]", "1"),
            ("ajax_page_state[css][misc/ui/jquery.ui.accordion.css]", "1"),
            (
                "ajax_page_state[css][sites/all/modules/contrib/date/date_api/date.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/date/date_popup/themes/datepicker.1.7.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/custom/fcbi_form_elements/resources/css/fcbi_form_element.css]",
                "1",
            ),
            ("ajax_page_state[css][modules/field/theme/field.css]", "1"),
            (
                "ajax_page_state[css][sites/all/modules/custom/fcbi/live_chat/resources/css/live_chat.css]",
                "1",
            ),
            ("ajax_page_state[css][modules/node/node.css]", "1"),
            ("ajax_page_state[css][modules/search/search.css]", "1"),
            ("ajax_page_state[css][modules/user/user.css]", "1"),
            (
                "ajax_page_state[css][sites/all/modules/contrib/extlink/css/extlink.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/views/css/views.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/ckeditor/css/ckeditor.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/ctools/css/ctools.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/panels/css/panels.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/libraries/qtip/jquery.qtip.min.css]", "1"),
            ("ajax_page_state[css][sites/all/modules/contrib/qtip/css/qtip.css]", "1"),
            ("ajax_page_state[css][modules/locale/locale.css]", "1"),
            (
                "ajax_page_state[css][https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.4.0/css/font-awesome.min.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/tb_megamenu/css/bootstrap.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/tb_megamenu/css/base.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/tb_megamenu/css/default.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/modules/contrib/tb_megamenu/css/compatibility.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/views.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/messages.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_sirate/css/html-elements.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/forms.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/page.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/articles.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/comments.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/forum.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/fields.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/blocks.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_sirate/css/panel-panes.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/themes/tb_sirate/css/navigation.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/fonts.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/css3.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_html-elements.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_forms.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_page.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_articles.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_blocks.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_views.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_quicktabs.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/mforms.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_fonts.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/tb_fnbt_megamenu.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_css3.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/overrides.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/nucleus/nucleus/css/responsive/responsive.css]",
                "1",
            ),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/print.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/css/fnbt_print.css]", "1"),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/screens/mobile.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/screens/mobile-vertical.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/screens/tablet-vertical.css]",
                "1",
            ),
            (
                "ajax_page_state[css][sites/all/themes/tb_fnbt/css/screens/tablet.css]",
                "1",
            ),
            ("ajax_page_state[css][public://nucleus/grid-fixed-12-972px.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/nucleus/nucleus/css/ie7.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/nucleus/nucleus/css/ie.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/ie.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_sirate/css/ie8.css]", "1"),
            ("ajax_page_state[css][sites/all/themes/tb_fnbt/]", "1"),
            ("ajax_page_state[js][0]", "1"),
            ("ajax_page_state[js][1]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/jquery/1.10/jquery.min.js]",
                "1",
            ),
            ("ajax_page_state[js][misc/jquery-extend-3.4.0.js]", "1"),
            ("ajax_page_state[js][misc/jquery-html-prefilter-3.5.0-backport.js]", "1"),
            ("ajax_page_state[js][misc/jquery.once.js]", "1"),
            ("ajax_page_state[js][misc/drupal.js]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/ui/ui/minified/jquery.ui.core.min.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/ui/ui/minified/jquery.ui.widget.min.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/ui/external/jquery.cookie.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/misc/jquery.form.min.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/replace/ui/ui/minified/jquery.ui.accordion.min.js]",
                "1",
            ),
            ("ajax_page_state[js][misc/ajax.js]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/jquery_update/js/jquery_update.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/custom/fcbi_form_elements/resources/js/fcbi_form_element.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/libraries/qtip/jquery.qtip.min.js]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/ctools/js/auto-submit.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/modules/contrib/views/js/base.js]", "1"),
            ("ajax_page_state[js][misc/progress.js]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/views/js/ajax_view.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/tb_megamenu/js/tb-megamenu-frontend.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/tb_megamenu/js/tb-megamenu-touch.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/google_analytics/googleanalytics.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/modules/contrib/bu/bu.js]", "1"),
            (
                "ajax_page_state[js][sites/all/modules/contrib/extlink/js/extlink.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/modules/contrib/quicktabs/js/qt_accordion.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/modules/contrib/qtip/js/qtip.js]", "1"),
            (
                "ajax_page_state[js][sites/all/themes/nucleus/nucleus/js/jquery.cookie.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/themes/tb_sirate/js/jquery-migrate-1.2.1.js]",
                "1",
            ),
            (
                "ajax_page_state[js][sites/all/themes/tb_sirate/js/jquery.matchHeights.min.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/themes/tb_sirate/js/tb_sirate.js]", "1"),
            (
                "ajax_page_state[js][sites/all/themes/tb_sirate/js/tb_responsive.js]",
                "1",
            ),
            ("ajax_page_state[js][sites/all/themes/tb_sirate/js/tb.plugins.js]", "1"),
            ("ajax_page_state[js][misc/tableheader.js]", "1"),
            ("ajax_page_state[jquery_version]", "1.10"),
        ]

        data.append(("page", str(count)))
        data.append(("view_dom_id", view_dom_id))
        data.append(("ajax_page_state[theme_token]", theme_token))

        session = SgRequests()
        stores_req = session.post(
            "https://www.1stnb.com/views/ajax", headers=headers, data=data
        )
        if status in stores_req.text:
            while status in stores_req.text:
                try:
                    log.info("Retrying due to CAPTCHA")
                    session = SgRequests()
                    stores_req = session.post(
                        "https://www.1stnb.com/views/ajax", headers=headers, data=data
                    )
                except:
                    pass

        json_data = json.loads(BS(stores_req.text, "html.parser").get_text())
        for data in json_data:
            if "method" in data:
                if "replaceWith" == data["method"]:
                    stores_sel = lxml.html.fromstring(data["data"])
                    break

        stores = stores_sel.xpath("//table/tbody/tr/td[1]/strong/a/@href")

        for store in stores:
            page_url = "https://www.1stnb.com" + store
            session = SgRequests()
            store_req = session.get(page_url, headers=headers)

            if status in store_req.text:
                while status in store_req.text:
                    try:
                        log.info("Retrying due to CAPTCHA")
                        session = SgRequests()
                        store_req = session.get(page_url, headers=headers)
                    except:
                        pass

            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h2[@class="node-title"]/text()')
            ).strip()

            street_address = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "address field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()
            city = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "city field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()
            state = "".join(
                store_sel.xpath(
                    '//div[@class="field field-name-field-state '
                    "field-type-taxonomy-term-reference field-label-hidden "
                    'clearfix"]/ul/li/text()'
                )
            ).strip()
            zip = "".join(
                store_sel.xpath(
                    '//div[@class="section field field-name-field-'
                    "zip-code field-type-text "
                    'field-label-hidden"]/div[1]/div[1]/text()'
                )
            ).strip()

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if len(zip) <= 0:
                zip = "".join(
                    store_sel.xpath('//span[@itemprop="postalCode"]/text()')
                ).strip()

            if zip == "":
                zip = "<MISSING>"

            country_code = ""
            if us.states.lookup(state):
                country_code = "US"

            if country_code == "":
                country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = "<MISSING>"

            location_type = "Branch"
            hours = store_sel.xpath(
                '//div[@class="section field '
                "field-name-field-operating-hours field-type-text-"
                "long "
                'field-label-above"]/div[1]/div[1]/p//text()'
            )

            final_hours = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    final_hours.append(
                        "".join(hour).strip().replace("\xa0", "").strip()
                    )
            hours_of_operation = " ".join(final_hours)

            map_link = "".join(
                store_sel.xpath('//div[@class="location map-link"]/a/@href')
            ).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if map_link:
                latitude = map_link.split("?q=")[1].strip().split("+")[0].strip()
                longitude = (
                    map_link.split("?q=")[1]
                    .strip()
                    .split("+", 1)[1]
                    .strip()
                    .split("+")[0]
                    .strip()
                )

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"

            curr_list = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            loc_list.append(curr_list)

        next_page = "".join(stores_sel.xpath('//li[@class="pager-next last"]/a/@href'))
        if len(next_page) > 0:
            count = count + 1
        else:
            break  # to get out of the while loop

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
