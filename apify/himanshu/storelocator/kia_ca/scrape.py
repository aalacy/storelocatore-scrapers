# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.kia.ca/content/marketing/ca/en/shopping-tools/find-a-dealer/jcr:content/root/container/container/section_container_1235319178/find_a_dealer.dealership.json?_postalCode={}"
    domain = "kia.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=50
    )
    for code in all_codes:
        all_locations = session.get(
            start_url.format(code.replace(" ", "")), headers=hdr
        )
        if all_locations.status_code != 200:
            continue
        all_locations = all_locations.json()
        for poi in all_locations:
            mon = f"Monday {poi['dealership']['openingHours']['mondayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['mondayClose'].split(':00.000')[0]}"
            tue = f"Tuesday {poi['dealership']['openingHours']['tuesdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['tuesdayClose'].split(':00.000')[0]}"
            wed = f"Wednesday {poi['dealership']['openingHours']['wednesdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['wednesdayClose'].split(':00.000')[0]}"
            thu = f"Thursday {poi['dealership']['openingHours']['thursdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['thursdayClose'].split(':00.000')[0]}"
            fri = f"Friday {poi['dealership']['openingHours']['fridayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['fridayClose'].split(':00.000')[0]}"
            if poi["dealership"]["openingHours"].get("saturdayOpen"):
                sat = f"Saturdayb {poi['dealership']['openingHours']['saturdayOpen'].split(':00.000')[0]} - {poi['dealership']['openingHours']['saturdayClose'].split(':00.000')[0]}"
            else:
                sat = ""
            hoo = f"{mon} {tue} {wed} {thu}, {fri} {sat}".strip()

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.kia.ca/en/shopping-tools/find-a-dealer",
                location_name=poi["dealership"]["name"],
                street_address=f"{poi['dealership']['dealershipAddress']['streetNumber']} {poi['dealership']['dealershipAddress']['street']}",
                city=poi["dealership"]["dealershipAddress"]["city"],
                state=poi["dealership"]["dealershipAddress"]["province"],
                zip_postal=poi["dealership"]["dealershipAddress"]["postalCode"],
                country_code=poi["dealership"]["dealershipAddress"].get("country"),
                store_number=poi["dealership"]["code"],
                phone=poi["dealership"]["phone"],
                location_type="",
                latitude=poi["dealership"]["latitude"],
                longitude=poi["dealership"]["longitude"],
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
