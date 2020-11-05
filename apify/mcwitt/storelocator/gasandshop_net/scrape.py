import csv
import re
from typing import NamedTuple, Optional, Tuple

from lxml import etree
import lxml.html
from parsy import Parser, decimal_digit, regex, seq, string
from sgrequests import SgRequests

URL = "http://www.gasandshop.net/general/location.aspx"


class Row(NamedTuple):
    locator_domain: str
    page_url: str
    location_name: str
    street_address: str
    city: str
    state: str
    zip: str
    country_code: str
    store_number: str
    phone: str
    location_type: str
    latitude: float
    longitude: float
    hours_of_operation: str


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(Row._fields)

        # Body
        for row in data:
            writer.writerow(row)


def _city_state_zip() -> Parser:
    title_word = regex("[A-Z][a-z]*")
    city = title_word.sep_by(string(" ")).map(" ".join)
    state = (regex("[A-Z]") * 2).concat()
    zip = (decimal_digit * 5).concat().map(int)
    return seq(city << string(", "), state << string(" "), zip)


def _extract_latlon(s: str) -> Tuple[float, float]:
    match = re.search(r"lat=(?P<lat>\d{2}\.\d{6})&lon=(?P<lon>-\d{3}\.\d{6})", s)
    if not match:
        raise RuntimeError(f"Failed to extract latitude, longitude from {s}")
    return float(match["lat"]), float(match["lon"])


def _get_location_type(name: str) -> Optional[str]:
    location_types = ["Gas & Shop", "Chevron"]
    try:
        return next(lt for lt in location_types if name.endswith(lt))
    except StopIteration:
        return None


def _parse_item(item: etree.Element) -> Row:

    location_name = item.xpath(
        "./span[@class='list_right']/div[@class='list_right_title']/a"
    )[0].text.strip()

    location_type = _get_location_type(location_name)

    city, state, zip = _city_state_zip().parse(
        item.xpath("./span[@class='list_right']/p/br")[0].tail.strip()
    )

    latitude, longitude = _extract_latlon(
        item.xpath("./span[@class='list_left']/a")[0].get("href")
    )

    return Row(
        locator_domain="gasandshop.net",
        page_url=URL,
        location_name=location_name,
        street_address=item.xpath("./span[@class='list_right']/p")[0].text.strip(),
        city=city,
        state=state,
        zip=zip,
        country_code="US",
        store_number=item.xpath("./span[@class='list_left']/a")[0].text.strip(),
        phone="<MISSING>",
        location_type=location_type if location_type is not None else "<MISSING>",
        latitude=latitude,
        longitude=longitude,
        hours_of_operation="<MISSING>",
    )


def fetch_data():

    session = SgRequests()
    response = session.get(URL)
    html = lxml.html.document_fromstring(response.text)
    list_items = html.xpath(
        "//div[@class='location_contain']/div[@class='contain_left']/div/span/ul/li"
    )

    if not list_items:
        raise RuntimeError("Empty list of locations")

    return [_parse_item(item) for item in list_items]


def scrape():
    data = fetch_data()
    write_output(data)
    print(baz)


if __name__ == "__main__":
    scrape()
