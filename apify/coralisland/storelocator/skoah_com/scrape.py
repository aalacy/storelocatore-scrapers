from lxml import etree

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

base_url = "https://skoah.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    url = "https://www.skoah.com/pages/our-locations"
    session = SgRequests()
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="css-grid__item location__item"]')
    for i in store_list:
        store = eliminate_space(i.xpath(".//text()"))
        output = []
        output.append(base_url)  # url
        link = base_url + i.xpath("a/@href")[0]
        output.append(link)
        output.append(store[0])  # location name
        output.append(store[1])  # address
        address = store[2].strip().split(",")
        output.append(address[0])  # city
        state_zip = address[1].strip().split(" ")
        output.append(state_zip[0])  # state
        output.append(validate(state_zip[1:]))  # zipcode
        if len(state_zip) == 2:
            output.append("US")  # country code
        else:
            output.append("CA")
        output.append("<MISSING>")  # store_number
        output.append(store[3])  # phone
        output.append("<MISSING>")  # location type

        request = session.get(link, headers=headers)
        response = etree.HTML(request.text)
        map_link = response.xpath('//a[@class="btn btn--primary"]/@href')[-1]
        if "@" in map_link:
            at_pos = map_link.rfind("@")
            latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
            longitude = map_link[
                map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
            ].strip()
        else:
            latitude = ""
            longitude = ""
        output.append(latitude)  # latitude
        output.append(longitude)  # longitude
        output.append(validate(store[5:-2]))  # opening hours

        sgw.write_row(
            SgRecord(
                locator_domain=output[0],
                page_url=output[1],
                location_name=output[2],
                street_address=output[3],
                city=output[4],
                state=output[5],
                zip_postal=output[6],
                country_code=output[7],
                store_number=output[8],
                phone=output[9],
                location_type=output[10],
                latitude=output[11],
                longitude=output[12],
                hours_of_operation=output[13],
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
