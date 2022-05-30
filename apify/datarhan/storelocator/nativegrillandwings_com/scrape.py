from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "nativegrillandwings.com"
    start_urls = [
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=HIUPWBZHHECLPKJH&center=33.4073,-111.9173&coordinates=31.95092540473827,-110.29681660156218,34.839662199081715,-113.53778339843724&multi_account=false&page=1&pageSize=30",
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=HIUPWBZHHECLPKJH&center=31.545571,-110.277225&coordinates=30.059382181489738,-108.65674160156257,33.00846630564875,-111.8977083984376&multi_account=false&page=1&pageSize=30",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    all_locations = []
    for url in start_urls:
        all_locations += session.get(url, headers=headers).json()

    with SgFirefox() as driver:
        for poi in all_locations:
            driver.get(poi["store_info"]["website"])
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//div[@class="hours-body ng-scope"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            sub_name = [
                e["data"] for e in poi["custom_fields"] if e["name"] == "geomodifier"
            ][0]

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["store_info"]["website"],
                location_name=poi["store_info"]["name"] + f" ({sub_name})",
                street_address=poi["store_info"]["address"],
                city=poi["store_info"]["locality"],
                state=poi["store_info"]["region"],
                zip_postal=poi["store_info"]["postcode"],
                country_code=poi["store_info"]["country"],
                store_number="",
                phone=poi["store_info"]["phone"],
                location_type="",
                latitude=poi["store_info"]["latitude"],
                longitude=poi["store_info"]["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
