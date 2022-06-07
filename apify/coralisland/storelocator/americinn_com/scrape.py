import json

from bs4 import BeautifulSoup
from lxml import etree

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

import usaddress

base_url = "https://www.wyndhamhotels.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    while True:
        if item[-1:] == " ":
            item = item[:-1]
        else:
            break
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


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    state = ""
    zipcode = ""
    country = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        elif addr[1] == "CountryName":
            country = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "

    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
        "country": get_value(country),
    }


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    url = "https://www.wyndhamhotels.com/americinn/locations"
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath(
        '//div[@class="state-container"]//li[@class="property"]'
    )
    for detail_url in store_list:
        detail_url = validate(detail_url.xpath(".//a")[0].xpath("./@href"))
        link = "https://www.wyndhamhotels.com" + detail_url
        detail_request = session.get(link, headers=headers)
        detail = etree.HTML(detail_request.text)

        address = validate(
            detail.xpath('.//div[contains(@class, "property-address")]//text()')
        )
        address = parse_address(address)

        if address["street"] == "<MISSING>":
            continue
        phone = validate(
            detail.xpath('.//div[contains(@class, "property-phone")]')[0].xpath(
                ".//text()"
            )
        ).replace("-", "")
        store_id = validate(
            detail_request.text.split('var overview_propertyId = "')[1].split('"')[0]
        )

        other_detail = BeautifulSoup(detail_request.text, "lxml")
        script = (
            other_detail.find("script", attrs={"type": "application/ld+json"})
            .contents[0]
            .replace("\t", "")
            .strip()
        )
        detail = json.loads(script)
        title = detail["name"]
        latitude = detail["geo"]["latitude"]
        longitude = detail["geo"]["longitude"]
        hours = "24 hours open"

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=link,
                location_name=title,
                street_address=address["street"],
                city=address["city"],
                state=address["state"],
                zip_postal=address["zipcode"],
                country_code="US",
                store_number=store_id,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
