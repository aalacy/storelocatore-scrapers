import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_phone(page_url) -> str:
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    return "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spiceandtea.com"
    api_url = "https://www.spiceandtea.com/where-to-buy"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations: ")[1]
        .replace("\n", "")
        .strip()
    )
    block = " ".join(block.split()).split(", imageLocations:")[0].strip()

    js = json.loads(block)

    for j in js["items"]:
        ids = j.get("id")
        info = j.get("popup_html")
        a = html.fromstring(info)
        text = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
        street_address = text.split("Address:")[1].split("State:")[0].strip()
        city = text.split("City:")[1].split("Zip:")[0].strip()
        postal = text.split("Zip:")[1].split("Address:")[0].strip()
        if postal.find("*") != -1:
            postal = postal.replace("*", "").strip()
        state = text.split("State:")[1].split("Description:")[0].strip()
        country_code = "US"
        location_name = "".join(
            a.xpath('//div[@class="amlocator-title"]/text()')
        ).strip()
        latitude = j.get("lat")
        longitude = j.get("lng")

        page_url = "".join(
            tree.xpath(f'//div[@data-amid="{ids}"]//a[@class="more-info"]/@href')
        ).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    f'//div[@data-amid="{ids}"]//div[@class="amlocator-schedule-table"]/div/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = get_phone(page_url) or "<MISSING>"
        if phone == "Coming Soon":
            phone = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
