import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://api.prooil.ca/api/stores/states/"
    domain = "take5oilchange.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    for state in data["message"]:
        for city in state["cities"]:
            all_locations = city["stores"]
            for poi in all_locations:
                store_url = poi["storeURL"]
                if not store_url:
                    store_url = (
                        "https://www.take5oilchange.ca/locations/{}/{}-{}/".format(
                            poi["locationState"],
                            poi["locationCity"],
                            str(poi["storeId"]),
                        )
                    )
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = "TAKE 5 OIL CHANGE #{}".format(str(poi["storeId"]))
                street_address = poi["streetAddress1"]
                city = poi["locationCity"]
                state = poi["locationState"]
                zip_code = poi["locationPostalCode"]
                country_code = poi["locationCountry"]
                store_number = poi["storeId"]
                phone = poi["phone"]
                location_type = "<MISSING>"
                latitude = poi["lat"]
                longitude = poi["lng"]
                hoo = []
                if store_url != "":
                    hoo = loc_dom.xpath(
                        '//div[@class="store-hours font-opensans font-16"]/p/text()'
                    )
                    hoo = [" ".join([s for s in e.split()]) for e in hoo if e.strip()]
                hours_of_operation = " ".join(hoo) if hoo else ""

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
