from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from lxml import etree

base_url = "https://www.roscoeschickenandwaffles.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def fetch_data(sgw: SgWriter):
    url = "https://www.roscoeschickenandwaffles.com/locations-and-hours"
    session = SgRequests()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath(
        '//div[@class="col sqs-col-3 span-3"]//div[@class="sqs-block-content"]'
    )
    for store in store_list:
        store = eliminate_space(store.xpath(".//text()"))
        output = []
        output.append(base_url)  # url
        output.append(store[0])  # location name
        output.append(store[1])  # address
        output.append("<MISSING>")  # city
        output.append("<MISSING>")  # state
        output.append("<MISSING>")  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        phone = ""
        store_hours = ""
        if len(store) > 3:
            phone = store[2]
            store_hours = validate(store[4:])
        output.append(phone)  # phone
        output.append("Roscoe's House Of Chicken And Waffles")  # location type
        output.append("<MISSING>")  # latitude
        output.append("<MISSING>")  # longitude
        output.append(store_hours)  # opening hours
        if store_hours:
            sgw.write_row(
                SgRecord(
                    locator_domain=base_url,
                    page_url=url,
                    location_name=store[0],
                    street_address=store[1],
                    city="",
                    state="",
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
