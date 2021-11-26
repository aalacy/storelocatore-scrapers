# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import pandas as pd

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.toyotaqatar.com/conf/data_master/m_dealer.csv"
    domain = "toyotaqatar.com"
    data = pd.read_csv(start_url)
    for index, poi in data.iterrows():
        geo = poi["position"].split(", ")
        hoo = " ".join([e.strip() for e in poi["hours"].split()])
        if hoo.startswith("|"):
            hoo = hoo[1:]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyotaqatar.com/find-a-dealer",
            location_name=poi["name"],
            street_address=poi["addr"],
            city="",
            state="",
            zip_postal="",
            country_code="Qatar",
            store_number="",
            phone=poi["tel"],
            location_type=poi["cat"],
            latitude=geo[0],
            longitude=geo[1],
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
