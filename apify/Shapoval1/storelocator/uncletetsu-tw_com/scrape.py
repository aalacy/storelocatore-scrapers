from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.uncletetsu-tw.com"
    api_url = "https://www.uncletetsu-tw.com/shop"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@href, "/shop")]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h2//text()"))
        phone = (
            "".join(
                tree.xpath(
                    '//*[contains(text(), "電話番号")]/text() | //span[contains(text(), "TEL:")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if phone.find("營業時間(") != -1:
            phone = phone.split("營業時間(")[0].strip()
        phone = phone.replace("電話番号：", "").replace("TEL:", "").strip()
        ad = (
            " ".join(
                tree.xpath(
                    f'//*[contains(text(), "{phone}")]/preceding::span[./text()]/text()'
                )
            )
            .replace("住所：", "")
            .strip()
        )
        if ad.find("開店時間") != -1:
            ad = ad.split("開店時間")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "TW"
        city = a.city or "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//*[contains(text(), ":00")]/text() | //*[contains(text(), "營業時間")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath('//*[contains(text(), "TEL:")]/text()'))
                .replace("\n", "")
                .strip()
            )
        if hours_of_operation.find("開店時間：") != -1:
            hours_of_operation = hours_of_operation.split("開店時間：")[1].strip()
        if hours_of_operation.find("營業時間(同微風廣場)") != -1:
            hours_of_operation = hours_of_operation.split("營業時間(同微風廣場)")[1].strip()
        if hours_of_operation.find("營業時間(同微風台北車站)") != -1:
            hours_of_operation = hours_of_operation.split("營業時間(同微風台北車站)")[1].strip()
        if hours_of_operation.find('"') != -1:
            hours_of_operation = hours_of_operation.split('"')[0].strip()
        if hours_of_operation.find("營業時間(同漢神巨蛋購物廣場)") != -1:
            hours_of_operation = hours_of_operation.split("營業時間(同漢神巨蛋購物廣場)")[1].strip()
        if hours_of_operation.find("TEL") != -1:
            hours_of_operation = (
                hours_of_operation.split("營業時間(同漢神百貨)")[1].split("徹思叔叔的店")[0].strip()
            )

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
