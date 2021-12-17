from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from lxml import etree

base_url = "https://bosstruckshops.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    while True:
        if item[-1:] == " ":
            item = item[:-1]
        else:
            break
    return item.strip()


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def fetch_data(sgw: SgWriter):
    url = "https://bosstruckshops.com/locations-by-state/"
    requests = SgRequests()
    request = requests.get(url)
    response = etree.HTML(request.text)
    store_url_list = response.xpath(
        '//article//li[contains(@class, "menu-item")]//a/@href'
    )

    for store_url in store_url_list:
        store_request = requests.get(store_url)
        store = etree.HTML(store_request.text)

        title = validate(store.xpath(".//h1//text()")[0])[:-1]
        info = store.xpath(
            './/div[contains(@class, "et_pb_section_1")]//div[@class="et_pb_text_inner"]'
        )
        phone = eliminate_space(info[0].xpath(".//text()")).pop()
        hours = (
            eliminate_space(info[0].xpath(".//text()"))[2].replace("Open:", "").strip()
        )
        if title == "Myerstown, Pennsylvani":
            hours = (
                eliminate_space(info[0].xpath(".//text()"))[1]
                .replace("Open:", "")
                .strip()
            )
        location_type = "Location"
        if "Unit" in hours:
            location_type = hours
            hours = ""

        city_state_zip = eliminate_space(info[2].xpath(".//text()"))[1].split(", ")
        city = city_state_zip.pop(0)
        if len(city_state_zip) == 1:
            state = city_state_zip[0].split(" ")[0]
            zipcode = city_state_zip[0].split(" ")[1]
        else:
            state = city_state_zip[0]
            zipcode = city_state_zip[1]
        street_address = eliminate_space(info[2].xpath(".//text()"))[0]
        geoinfo = validate(
            store.xpath('.//div[contains(@class, "et_pb_section_1")]//a/@href').pop()
        )
        latitude = geoinfo.split("@")[1].split(",")[0]
        longitude = geoinfo.split("@")[1].split(",")[1]

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=store_url,
                location_name=title,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code="US",
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
