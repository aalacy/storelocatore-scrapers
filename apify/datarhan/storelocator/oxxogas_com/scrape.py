# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
import demjson

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = (
        "https://www.google.com/maps/d/u/2/embed?mid=1pveBX3BRSJhoYDPGP-zdFz8XbvaSnWmV"
    )
    domain = "oxxogas.com"
    response = session.get(start_url)
    data = response.text.split("var _pageData = ")[-1].split(";</script>")[0]
    data = demjson.decode(data)
    data = json.loads(data)

    for poi in data[1][6][0][12][0][13][0]:
        raw_addr = poi[5][-1][-1][1][0]
        addr = parse_address_intl(raw_addr)
        state = poi[5][-1][0][1][0]
        street_address = raw_addr.split(state)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url="http://oxxogas.com/estaciones/",
            location_name=poi[5][0][1][0],
            street_address=street_address,
            city=addr.city,
            state=state,
            zip_postal=addr.postcode,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi[5][-1][3][1][0],
            longitude=poi[5][-1][4][1][0],
            hours_of_operation=SgRecord.MISSING,
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
