from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "action": "csl_ajax_onload",
    "address": "",
    "formdata": "addressInput=",
    "lat": "43.735215",
    "lng": "-79.4196338",
    "options[distance_unit]": "km",
    "options[dropdown_style]": "none",
    "options[hide_search_form]": "true",
    "options[ignore_radius]": "0",
    "options[immediately_show_locations]": "1",
    "options[initial_radius]": "",
    "options[label_directions]": "Directions",
    "options[label_email]": "Email",
    "options[label_fax]": "Fax",
    "options[label_phone]": "Phone",
    "options[label_website]": "Website",
    "options[loading_indicator]": "",
    "options[map_center]": "1999 Avenue Rd, North York, Ontario M5M 4A5",
    "options[map_center_lat]": "43.735215",
    "options[map_center_lng]": "-79.4196338",
    "options[map_domain]": "maps.google.ca",
    "options[map_end_icon]": "https://www.firkinpubs.com/wp-content/plugins/store-locator-le/images/icons/bulb_red-dot.png",
    "options[map_home_icon]": "https://www.firkinpubs.com/wp-content/plugins/store-locator-le/images/icons/blank.png",
    "options[map_region]": "ca",
    "options[map_type]": "roadmap",
    "options[no_autozoom]": "0",
    "options[use_sensor]": "false",
    "options[zoom_level]": "4",
    "options[zoom_tweak]": "0",
}


def _hours(val):
    hours_of_operation = val.replace("Hours", "").replace("|", ";").strip()
    if hours_of_operation.startswith(":"):
        hours_of_operation = hours_of_operation[1:]

    return hours_of_operation


def fetch_data():
    locator_domain = "https://www.firkinpubs.com/"
    base_url = "https://www.firkinpubs.com/find-your-local-firkin/"
    ajax_url = "https://www.firkinpubs.com/wp-admin/admin-ajax.php"
    with SgRequests() as session:
        locations = session.post(ajax_url, headers=_headers, data=data).json()
        for _ in locations["response"]:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"] or "Canada",
                latitude=_["lat"],
                longitude=_["lng"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_hours(_["hours"]),
            )
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.other-loc div.slp_results_container")
        for _ in locations:
            street_address = f"{_.select_one('span.slp_result_street').text} {_.select_one('span.slp_result_street2').text}"
            city_state = _.select_one("span.slp_result_citystatezip").text
            state_zip = city_state.split(",")[1].strip().split(" ")
            coord = (
                _.select(".results_wrapper")[1]
                .a["href"]
                .split("/@")[1]
                .split("z/")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one("span.location_name").text,
                store_number=_.select_one(".results_wrapper")["id"].split("_")[-1],
                street_address=street_address,
                city=city_state.split(",")[0],
                state=state_zip[0],
                zip_postal=" ".join(state_zip[1:]),
                country_code=_.select_one("span.slp_result_country").text,
                latitude=coord[0],
                longitude=coord[1],
                phone=_.select_one("span.slp_result_phone").text,
                locator_domain=locator_domain,
                hours_of_operation=_hours(_.select_one("span.slp_result_hours").text),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
