from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "redribbonbakeshop.us",
    "Origin": "https://redribbonbakeshop.us",
    "Referer": "https://redribbonbakeshop.us/store-locator/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "action": "csl_ajax_onload",
    "address": "",
    "formdata": "addressInput=",
    "lat": "36.778261",
    "lng": "-119.4179324",
    "options[distance_unit]": "miles",
    "options[dropdown_style]": "none",
    "options[ignore_radius]": "0",
    "options[immediately_show_locations]": "1",
    "options[initial_radius]": "",
    "options[label_directions]": "Directions",
    "options[label_email]": "Email",
    "options[label_fax]": "Fax",
    "options[label_phone]": "Phone",
    "options[label_website]": "Website",
    "options[loading_indicator]": "",
    "options[map_center]": "California, US",
    "options[map_center_lat]": "36.778261",
    "options[map_center_lng]": "-119.4179324",
    "options[map_domain]": "maps.google.com",
    "options[map_end_icon]": "/wp-content/plugins/store-locator-le/images/icons/bulb_red.png",
    "options[map_home_icon]": "/wp-content/plugins/store-locator-le/images/icons/blank.png",
    "options[map_region]": "us",
    "options[map_type]": "roadmap",
    "options[no_autozoom]": "0",
    "options[use_sensor]": "false",
    "options[zoom_level]": "12",
    "options[zoom_tweak]": "0",
}


def fetch_data():
    locator_domain = "https://redribbonbakeshop.us/"
    page_url = "https://redribbonbakeshop.us/store-locator/"
    base_url = "https://redribbonbakeshop.us/wp-admin/admin-ajax.php"
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, data=data).json()
        for _ in locations["response"]:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["zip"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["hours"].strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
