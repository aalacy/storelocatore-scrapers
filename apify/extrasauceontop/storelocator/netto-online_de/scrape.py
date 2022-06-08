from sgrequests import SgRequests
from lxml import etree
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    url = "https://www.netto-online.de/INTERSHOP/web/WFS/Plus-NettoDE-Site/de_DE/-/EUR/ViewNettoStoreFinder-GetStoreItems"
    domain = "netto-online.de"
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    params = {
        "s": "-90.0",
        "n": "90.0",
        "w": "-180.0",
        "e": "180.0",
        "netto": "false",
        "city": "false",
        "service": "false",
        "beverage": "false",
        "nonfood": "false",
    }

    while True:
        response_stuff = session.post(url, headers=headers, data=params)
        status = response_stuff.status_code
        if status != 200:
            continue

        else:
            break

    response = response_stuff.json()

    for poi in response["store_items"]:
        hoo = etree.HTML(poi["store_opening"]).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.netto-online.de/filialfinder",
            location_name=poi["store_name"],
            street_address=poi["street"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["post_code"],
            country_code="DE",
            store_number=poi["store_id"],
            phone="",
            location_type="",
            latitude=poi["coord_latitude"],
            longitude=poi["coord_longitude"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
