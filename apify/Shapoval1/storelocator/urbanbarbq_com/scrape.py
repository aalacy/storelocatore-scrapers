from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.urbanbarbq.com/"
    api_url = "https://www.urbanbarbq.com/Locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="lnkStoreName"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.urbanbarbq.com{slug}"
        store_id = page_url.split("=")[-1].strip()
        latitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{store_id}")]/text()'))
            .split("LatLng(")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{store_id}")]/text()'))
            .split("LatLng(")[-1]
            .split(",")[1]
            .split(")")[0]
            .strip()
        )

        r = session.get(page_url)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath('//div[@class="store-name"]/span/text()'))
        blink = "<MISSING>"
        if location_name.find("BWI Airport") != -1:
            blink = "".join(tree.xpath('//span[@class="blinkMe"]/text()')).strip()
        hours_of_operation = "<MISSING>"
        if blink != "<MISSING>":
            hours_of_operation = blink
        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        country_code = "US"
        line = "".join(
            tree.xpath('//div[@class="store-address-line2"]/text()')
        ).replace("-", " ")
        street_address = "".join(
            tree.xpath('//div[@class="store-address-line1"]/text()')
        )
        postal = line.split()[2]
        city = line.split()[0]
        state = line.split()[1]
        phone = "".join(tree.xpath('//span[@class="store-phone"]/text()'))

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
