from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "carrierenterprise.com"
    start_url = "https://www.carrierenterprise.com/graphql"

    frm = {
        "operationName": "getBranches",
        "query": "query getBranches($all_regions: Boolean, $lat: Float!, $lng: Float!, $num: Int, $radius: Float!) {\n  storeLocator(all_regions: $all_regions, lat: $lat, lng: $lng, num: $num, radius: $radius) {\n    geocode_lat\n    geocode_lng\n    stores {\n      after_hours_phone_1\n      after_hours_phone_2\n      after_hours_phone_3\n      branch_add1\n      branch_add2\n      branch_city\n      branch_id\n      branch_info_url\n      branch_name\n      branch_phone\n      branch_state\n      branch_zip\n      branch_mon_close\n      branch_mon_open\n      branch_tue_close\n      branch_tue_open\n      branch_wed_close\n      branch_wed_open\n      branch_thu_close\n      branch_thu_open\n      branch_fri_close\n      branch_fri_open\n      branch_sat_close\n      branch_sat_open\n      branch_sun_close\n      branch_sun_open\n      distance\n      id\n      latitude\n      longitude\n      marker_label\n      units\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {
            "all_regions": True,
            "lat": 37.09024,
            "lng": -95.712891,
            "num": 1000,
            "radius": 25000,
        },
    }
    data = session.post(start_url, json=frm).json()

    for poi in data["data"]["storeLocator"]["stores"]:
        if poi["branch_add2"]:
            street_address = poi["branch_add2"]
            location_type = poi["branch_add1"]
        else:
            street_address = poi["branch_add1"]
            location_type = ""
        store_number = poi["branch_id"]
        page_url = f"https://www.carrierenterprise.com/branches/{store_number}/{poi['branch_info_url'].split('/')[-1]}"

        mon = f'Monday: {poi["branch_mon_open"]} - {poi["branch_mon_close"]}'
        tue = f'Tuesday: {poi["branch_tue_open"]} - {poi["branch_tue_close"]}'
        wed = f'Wednesday: {poi["branch_wed_open"]} - {poi["branch_wed_close"]}'
        thu = f'Thursday: {poi["branch_thu_open"]} - {poi["branch_thu_close"]}'
        fri = f'Friday: {poi["branch_fri_open"]} - {poi["branch_fri_close"]}'
        sat = "Saturday: closed"
        if poi["branch_sat_open"]:
            sat = f'Saturday: {poi["branch_sat_open"]} - {poi["branch_sat_close"]}'
        sun = "Sunday: closed"
        if poi["branch_sun_open"]:
            sun = f'Sunday: {poi["branch_sun_open"]} - {poi["branch_sun_close"]}'
        hoo = ", ".join([mon, tue, wed, thu, fri, sat, sun])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["branch_name"],
            street_address=street_address,
            city=poi["branch_city"],
            state=poi["branch_state"],
            zip_postal=poi["branch_zip"],
            country_code="",
            store_number=store_number,
            phone=poi["branch_phone"],
            location_type=location_type,
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
