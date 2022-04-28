# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.bigbargaintas.com.au/wp-admin/admin-ajax.php"
    domain = "bigbargaintas.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "action": "csl_ajax_onload",
        "address": "",
        "formdata": "addressInput=",
        "lat": "-41.4545196",
        "lng": "145.9706647",
        "options[distance_unit]": "km",
        "options[dropdown_style]": "base",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "1",
        "options[initial_radius]": "800",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax: ",
        "options[label_phone]": "Phone: ",
        "options[label_website]": "More Details",
        "options[loading_indicator]": "",
        "options[map_center]": "Tasmania",
        "options[map_center_lat]": "-41.4545196",
        "options[map_center_lng]": "145.9706647",
        "options[map_domain]": "maps.google.com.au",
        "options[map_end_icon]": "http://www.bigbargaintas.com.au/wp-content/uploads/2013/07/bottlelogosmall.png",
        "options[map_home_icon]": "http://www.bigbargaintas.com.au/wp-content/plugins/store-locator-le/images/icons/blank.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "12",
        "options[zoom_tweak]": "0",
        "radius": "800",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["response"]:
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.bigbargaintas.com.au/store-finder/",
            location_name=poi["name"],
            street_address=street_address.replace(",", ""),
            city=poi["city"].replace(",", ""),
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="AU",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=poi["hours"]
            .replace("&lt;br/&gt;", "")
            .replace("\r\n", "")
            .split("&lt;strong")[0]
            .replace("&lt;/br&gt;", "")
            .split(", PUB HOL")[0]
            .split("PUB")[0],
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
