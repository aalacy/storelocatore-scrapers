from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from lxml import etree

base_url = "https://midwoodsmokehouse.com"


def fetch_data(sgw: SgWriter):
    url = "https://midwoodsmokehouse.com/locations/"
    session = SgRequests()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath(
        '//div[contains(@class, "locations-listing")]//div[@class="inside"]'
    )
    for store in store_list:
        title = store.xpath('.//div[@class="address-info"]//h3[@class="name"]/text()')[
            0
        ]
        street_address = store.xpath(
            './/div[@class="address-info"]//div[contains(@class, "add1")]//text()'
        )[0]
        city = store.xpath(
            './/div[@class="address-info"]//div[contains(@class, "add2")]//text()'
        )[0].split(",")[0]
        state = store.xpath(
            './/div[@class="address-info"]//div[contains(@class, "add2")]//text()'
        )[0].split(",")[1]
        phone = store.xpath(
            './/div[@class="address-info"]//div[@class="phone"]//text()'
        )[0]
        hours = " ".join(store.xpath('.//div[@class="hours"]//text()'))
        store_hours = (
            hours.replace("Hours", "")
            .replace("\n", "")
            .replace("\r \r", "")
            .replace("\r", "")
        )

        if store_hours:
            sgw.write_row(
                SgRecord(
                    locator_domain=base_url,
                    page_url=url,
                    location_name=title,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal="",
                    country_code="US",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude="",
                    longitude="",
                    hours_of_operation=store_hours,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
