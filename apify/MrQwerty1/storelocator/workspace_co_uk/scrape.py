import ssl
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


def get_data(_id):
    url = f"https://www.workspace.co.uk/propertysearchresultspage/propertysearchmodel?propertyCrmId={_id}"
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    name = tree.xpath("//h1[@class='property-search-modal__title']/text()").pop()
    raw_address = "".join(
        set(tree.xpath("//div[@class='property-search-modal__address']/text()"))
    )
    slug = tree.xpath("//a[contains(text(), 'More info')]/@href").pop()
    page_url = f"https://www.workspace.co.uk{slug}"

    return name, raw_address, page_url


def get_phone():
    ua = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"
    with SgChrome(user_agent=ua) as fox:
        fox.get(locator_domain)
        time.sleep(10)
        source = fox.page_source

    tree = html.fromstring(source)
    return "".join(set(tree.xpath("//span[contains(@class, 'number')]/text()")))


def fetch_data(sgw: SgWriter):
    api = "https://www.workspace.co.uk/api//map/get?maptype=0"
    r = session.get(api, headers=headers)
    js = r.json()

    phone = get_phone()
    for j in js:
        store_number = j.get("PropertyCrmId")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        location_name, raw_address, page_url = get_data(store_number)
        street_address = ",".join(raw_address.split(",")[:-1])
        city = "London"
        postal = raw_address.split(",")[-1].strip()
        country_code = "GB"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.workspace.co.uk/"
    ssl._create_default_https_context = ssl._create_unverified_context
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
