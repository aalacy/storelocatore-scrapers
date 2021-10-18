import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_tree(_id):
    data = {"action": "mmm_async_content_marker", "id": _id}
    r = session.post(
        "https://www.denisonyachtsales.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )

    return html.fromstring(r.text)


def fetch_data(sgw: SgWriter):
    api = "https://www.denisonyachtsales.com/contact-us/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var maps =')]/text()"))
    text = text.split('"markers":')[1].split("}];")[0]
    js = json.loads(text)

    for j in js:
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        d = get_tree(store_number)
        location_name = "".join(d.xpath("//h2/text()")).strip()
        page_url = "".join(d.xpath("//li[@class='weblink']//a/@href"))
        raw_address = "".join(d.xpath("//li[@class='adresse']//text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        country_code = "US"
        if "Hong" in raw_address:
            country_code = "HK"
        phone = "".join(d.xpath("//li[@class='telephone']//text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.denisonyachtsales.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
