from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.centura.org/location-search"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "location-search-result"})
    flag = 0
    for i in range(1, 60):
        myobj = {
            "view_name": "location_search",
            "view_display_id": "page",
            "view_args": "",
            "view_path": "/location-search",
            "view_base_path": "location-search",
            "view_dom_id": "d422d9a5cadb84de2e71bee42af2edfc4fb23f8f127959316f9f378d0849472c",
            "pager_element": "1",
            "type": "All",
            "service": "All",
            "page": "0," + str(i) + ",,0",
            "_drupal_ajax": "1",
            "ajax_page_state[theme]": "centura_theme",
            "ajax_page_state[theme_token]": "",
            "ajax_page_state[libraries]": "better_exposed_filters/auto_submit,better_exposed_filters/general,centura_geolocation/geolocate_user,centura_search/centura_search_api_autocomplete,centura_search/search_form,centura_search_react/location-app-controller,centura_theme/global-scripts,centura_theme/global-styling,classy/base,classy/messages,colorbox/plain,colorbox_inline/colorbox_inline,core/drupal.states,core/html5shiv,core/normalize,eu_cookie_compliance/eu_cookie_compliance_bare,social_media_links/fontawesome.component,social_media_links/social_media_links.theme,system/base,views/views.module,views_infinite_scroll/views-infinite-scroll",
        }

        url = "https://www.centura.org/views/ajax?_wrapper_format=drupal_ajax"
        r = session.post(url, headers=headers, data=myobj).json()[1]["data"]
        soup = BeautifulSoup(r, "html.parser")
        if flag == 0:
            loclist = loclist + soup.findAll("div", {"class": "location-search-result"})
            flag = 1
        else:
            loclist = soup.findAll("div", {"class": "location-search-result"})
        for loc in loclist:
            street = loc["data-address"] + " " + loc["data-address-two"]
            title = loc.find("div", {"class": "location-search-result__name"}).text
            lat, longt = loc["data-field-solr-lat-long"].split(",")
            city = loc["data-locality"]
            state = loc["data-admin"]
            store = loc["data-nid"]
            ltype = loc["data-type-name"]
            link = "https://www.centura.org" + loc["data-url"]
            phone = loc["data-phone"]
            r = session.get(link, headers=headers)
            try:
                pcode = r.text.split('"postalCode":"', 1)[1].split('"', 1)[0]
            except:
                try:
                    pcode = r.text.split('="postal-code">', 1)[1].split("<", 1)[0]
                except:
                    pcode = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.centura.org",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
                phone=phone.strip(),
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation="<MISSING>",
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
