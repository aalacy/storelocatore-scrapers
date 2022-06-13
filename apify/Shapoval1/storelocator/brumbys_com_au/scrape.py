from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.brumbys.com.au/"
    api_url = "https://www.brumbys.com.au/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "storesObj")]/text()'))
        .split('{"stores":"')[1]
        .split('","marker"')[0]
        .replace("\\", "")
        .strip()
    )
    js_block = (
        js_block.replace('"tel:"', "'tel:'")
        .replace('"tel', "'tel")
        .replace('9">', "9'>")
        .replace('6">', "6'>")
        .replace('7">', "7'>")
        .replace('5">', "5'>")
        .replace('0">', "0'>")
        .replace('2">', "2'>")
        .replace('3">', "3'>")
        .replace('8">', "8'>")
        .replace('1">', "1'>")
        .replace('4">', "4'>")
        .replace('""', '"')
    )
    js = eval(js_block)
    for j in js:

        a = j.get("address")
        ad = a.get("address")
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = b.state or "<MISSING>"
        postal = b.postcode or "<MISSING>"
        country_code = "AU"
        city = b.city or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="col-sm-6 store-left-detail"]//a[contains(@href, "tel")]/text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="col-sm-6 store-left-detail"]//h3[text()="Opening Hours"]/following-sibling::table//tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Christmas") != -1:
            hours_of_operation = hours_of_operation.split("Christmas")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
