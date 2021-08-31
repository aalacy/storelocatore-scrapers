from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://tacobell.co.jp"
    api_url = "http://tacobell.co.jp/#findus"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="icon-box-boxed top"]')
    for d in div:

        page_url = "http://tacobell.co.jp/#findus"
        location_name = "".join(d.xpath(".//h4/a/text()"))
        ad = " ".join(d.xpath("./p[1]/text()")).replace("\n", "").strip()

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "JP"
        city = a.city or "<MISSING>"
        phone = (
            " ".join(d.xpath("./p[3]/text()"))
            .replace("\n", "")
            .replace("電話番号:", "")
            .strip()
        )
        if phone.find("※一部対象外店舗あり") != -1:
            phone = "<MISSING>"
        if location_name == "Uber Eats":
            continue

        hours_of_operation = (
            " ".join(d.xpath("./p[2]/text()"))
            .replace("\n", "")
            .replace("営業時間:", "")
            .strip()
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
