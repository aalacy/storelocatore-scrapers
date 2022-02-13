import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.smoothieking.co.kr/"
    api_url = "https://www.shinsegaefood.com/smoothieking/store/store.sf"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var storelist =")]/text()'))
        .split("var storelist =")[1]
        .split("//console.dir(storelist);")[0]
        .strip()
    )
    js = json.loads(div)

    for j in js:
        brand_id = j.get("seq")
        sub_js_block = (
            "".join(tree.xpath('//script[contains(text(), "var storelist =")]/text()'))
            .split("var codeList =")[1]
            .split(";")[0]
            .strip()
        )
        sub_js = json.loads(sub_js_block)
        location_type = "<MISSING>"
        city = "<MISSING>"
        ref_code = ""
        for k in sub_js:
            code = k.get("code")
            if code == brand_id:
                location_type = k.get("codeName")
                ref_code = k.get("refCode")
        for c in sub_js:
            sub_ref_code = c.get("code")
            if sub_ref_code == ref_code:
                city = c.get("codeName")
        page_url = "https://www.smoothieking.co.kr/"
        location_name = j.get("title")
        info = j.get("brandDesc")
        a = html.fromstring(info)
        info_lst = a.xpath("//*//text()")
        info_lst = list(filter(None, [b.strip() for b in info_lst]))
        adr = "<MISSING>"
        for i in info_lst:
            if "주소 :" in i:
                adr = "".join(i).split("주소 :")[1].strip()

        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address.isdigit() or street_address == "<MISSING>":
            street_address = adr
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "KR"
        latlon = "".join(j.get("imgUrl"))
        latitude = latlon.split(",")[1].strip()
        longitude = latlon.split(",")[0].strip()
        if latitude == "1":
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        for i in info_lst:
            if "전화번호 :" in i:
                phone = "".join(i).replace("\xa0", "").split("전화번호 :")[1].strip()
        if phone.find("이마트24R상무유탑호텔") != -1:
            phone = "<MISSING>"
        phone = phone or "<MISSING>"

        hours_of_operation = "<MISSING>"
        for i in info_lst:
            if "영업시간 :" in i:
                hours_of_operation = (
                    "".join(i).replace("\xa0", "").split("영업시간 :")[1].strip()
                )
        if (
            hours_of_operation == "매장 문의 바랍니다."
            or hours_of_operation == "전화 문의 바랍니다."
            or hours_of_operation == "매장에 문의 바랍니다."
        ):
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("[") != -1:
            hours_of_operation = hours_of_operation.replace("[", "").strip()
        if hours_of_operation.find("]") != -1:
            hours_of_operation = hours_of_operation.replace("]", "").strip()
        if phone.find(" /") != -1:
            phone, hours_of_operation = hours_of_operation, phone

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
