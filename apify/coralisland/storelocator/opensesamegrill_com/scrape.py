from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from lxml import etree
import json

base_url = "https://www.opensesamegrill.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
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
    url = "https://www.opensesamegrill.com"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = json.loads(
        validate(response.xpath('.//script[@type="application/ld+json"]//text()')[0])
    )["subOrganization"]
    for store in store_list:
        location_name = get_value(store["name"])  # location name
        street_address = get_value(store["address"]["streetAddress"])  # address
        city = get_value(store["address"]["addressLocality"])  # city
        state = get_value(store["address"]["addressRegion"])  # state
        zip_code = get_value(store["address"]["postalCode"])  # zipcode
        country_code = "US"
        store_number = ""
        phone = get_value(store["telephone"])
        location_type = get_value(store["@type"])

        link = store["url"]
        req = session.get(link)
        base = BeautifulSoup(req.text, "lxml")

        latitude = base.find(class_="gmaps")["data-gmaps-lat"]
        longitude = base.find(class_="gmaps")["data-gmaps-lng"]
        store_hours = base.find(id="intro").get_text(" ").split("Hours")[-1].strip()

        sgw.write_row(
            SgRecord(
                locator_domain=url,
                page_url=link,
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
                hours_of_operation=store_hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
