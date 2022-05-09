from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.suzuki.nl/v1/dealers/?brand=SUZUKI)"
    domain = "suzuki.nl"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        if not poi["is_sales_dealer"]:
            continue
        page_url = urljoin("https://www.suzuki.nl", poi["detail_page_url"])
        street_address = poi["street_name"]
        if poi["house_number"]:
            street_address += " " + poi["house_number"]
        if poi["house_number_suffix"]:
            street_address += " " + poi["house_number_suffix"]
        if poi["showroom_hours_mon"]:
            mon = f'Mon {poi["showroom_hours_mon"]}'
        else:
            mon = "Mon Closed"
        if poi["showroom_hours_tue"]:
            tue = f'Tue {poi["showroom_hours_tue"]}'
        else:
            tue = "Tue Closed"
        if poi["showroom_hours_wed"]:
            wed = f'Wed {poi["showroom_hours_wed"]}'
        else:
            wed = "Wed Closed"
        if poi["showroom_hours_thu"]:
            thu = f'Thu {poi["showroom_hours_thu"]}'
        else:
            thu = "Thu Closed"
        if poi["showroom_hours_fri"]:
            fri = f'Fri {poi["showroom_hours_fri"]}'
        else:
            fri = "Fri Closed"
        sat = f'Sat {poi["showroom_hours_sat"]}'
        if poi["showroom_hours_sun"]:
            sun = f'Sun {poi["showroom_hours_sun"]}'
        else:
            sun = "Sun Closed"
        hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state="",
            zip_postal=poi["zipcode"],
            country_code="NL",
            store_number=poi["dealer_number"],
            phone=poi["display_phone_number"],
            location_type="",
            latitude=poi["location_lat"],
            longitude=poi["location_long"],
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
