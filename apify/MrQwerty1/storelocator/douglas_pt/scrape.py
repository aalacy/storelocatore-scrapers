import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.douglas.pt/StoreLocator/search"
    data = {
        'lat': '0',
        'lng': '0',
        'distance': '0',
        'input': '',
        'country': 'PT',
        'catFilter': '',
        'byname': '',
    }
    r = session.post(api, headers=headers, data=data)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-id]")

    for d in divs:
        store_number = "".join(d.xpath("./@data-id"))
        location_name = "".join(
            d.xpath(".//div[contains(@class, 'shopname')]/span/text()")
        ).strip()
        raw_address = "".join(
            d.xpath(".//div[contains(@class, 'address')]/span/text()")
        ).strip()
        print(raw_address)
        postal = "".join(re.findall(r"\d{4}.\d{3}", raw_address))
        street_address = raw_address.split(postal)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address.split(postal)[-1].strip()
        if "," in city:
            city = city.split(",")[0].strip()
        country_code = "PT"
        phone = "".join(d.xpath(".//span[contains(text(), 'Tel')]/a/text()")).strip()

        text = "".join(d.xpath("./following-sibling::script[1]/text()"))
        latitude = text.split(f"{store_number},")[1].split(",")[0].strip()
        longitude = text.split(f"{latitude},")[1].split(",")[0].strip()

        hours = d.xpath(".//div[contains(@class, 'hours')]/span/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

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
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.douglas.pt/"
    page_url = "https://www.douglas.pt/storeLocator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
