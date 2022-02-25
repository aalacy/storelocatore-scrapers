import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "doublekwik.com"
    start_url = "https://www.doublekwik.com/wp-admin/admin-ajax.php"
    formdata = {
        "action": "csl_ajax_onload",
        "address": "",
        "formdata": "addressInput=",
        "lat": "37.1219167",
        "lng": "-82.8295581",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "1",
        "options[initial_radius]": "10000",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax: ",
        "options[label_phone]": "Phone: ",
        "options[label_website]": "Website",
        "options[loading_indicator]": "",
        "options[map_center]": "Whitesburg, KY, US",
        "options[map_center_lat]": "37.1219167",
        "options[map_center_lng]": "-82.8295581",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "https://www.doublekwik.com/wp-content/plugins/store-locator-le/images/icons/pin_blue-pushpin.png",
        "options[map_home_icon]": "https://www.doublekwik.com/wp-content/plugins/store-locator-le/images/icons/bulb_red-dot.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "19",
        "options[zoom_tweak]": "0",
        "radius": "10000",
    }
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data["response"]:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        if street_address.startswith(","):
            street_address = street_address[1:]
        city = poi["city"]
        city = city.split(", ")[0] if city else "<MISSING>"
        state = poi["city_state_zip"].split(", ")[-1].split()[0]
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["hours"]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
