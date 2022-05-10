from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.fm.bank/wp-admin/admin-ajax.php?action=store_search&lat=41.52144&lng=-84.30717&max_results=10&search_radius=200&autoload=1"
    domain = "fm.bank"

    hdr = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = "https://www.fm.bank/locations/"
        location_name = poi["store"]
        location_name = (
            location_name.replace("&#8211;", "-")
            .replace("#038;", "")
            .replace("&#8217;", "'")
            if location_name
            else ""
        )
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = poi["cat_name"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = [
            poi["lobby_hours_l1"],
            poi["lobby_hours_v1"],
            poi["lobby_hours_l2"],
            poi["lobby_hours_v2"],
            poi["lobby_hours_l3"],
            poi["lobby_hours_v3"],
            poi["lobby_hours_l4"],
            poi["lobby_hours_v4"],
        ]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
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
