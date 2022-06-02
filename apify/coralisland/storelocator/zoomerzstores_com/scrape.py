import usaddress
from lxml import etree

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
base_url = "https://zoomerzstores.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


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
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


def fetch_data(sgw: SgWriter):
    url = "https://zoomerzstores.com/locations?radius=-1&filter_catid=0&limit=0&filter_order=distance&searchzip=Tennessee"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "32edeb25dad71c1c7dc8fbebd9de5d86=590499051483b07550207aad0c0b1b80; nrid=69257523a762df8d",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    formdata = {
        "searchzip": "You",
        "task": "search",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "223",
        "zoom": "9",
        "format": "json",
        "geo": "1",
        "limitstart": "0",
        "latitude": "37.09024",
        "longitude": "-95.712891",
    }
    store_list = session.post(url, headers=headers, data=formdata).json()["features"]

    for store in store_list:
        output = []
        output.append(base_url)
        output.append("https://zoomerzstores.com" + store["properties"]["url"])
        output.append(get_value(store["properties"]["name"]))
        addr = ", ".join(
            eliminate_space(
                etree.HTML(store["properties"]["fulladdress"]).xpath(".//text()")
            )[:-2]
        ).replace("United States", "")
        address = parse_address(addr)
        output.append(address["street"])
        if address["state"] != "<MISSING>":
            output.append(address["city"])
            output.append(address["state"])
        else:
            output.append(validate(address["city"].split(" ")[:-1]))
            output.append(validate(address["city"].split(" ")[-1]))
        output.append(address["zipcode"])
        output.append("US")
        output.append(get_value(store["id"]))
        output.append("<MISSING>")
        output.append("<MISSING>")
        output.append(get_value(store["geometry"]["coordinates"][0]))
        output.append(get_value(store["geometry"]["coordinates"][1]))
        output.append("<MISSING>")

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
                latitude=output[12],
                longitude=output[11],
                hours_of_operation=output[13],
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
