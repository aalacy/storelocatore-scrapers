import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ashley.cn"
    api_url = "https://ashley.cn/about/store"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var storeList")]/text()'))
        .split("var storeList = '")[1]
        .split("';")[0]
        .replace('"[', "[")
        .replace(']"', "]")
        .strip()
    )
    x = json.loads('{"foo": "% s"}' % div)
    x0 = x["foo"]
    x1 = eval(x0)

    for x in x1:

        page_url = "https://ashley.cn/about/store"
        location_name = x.get("title") or "<MISSING>"
        street_address = x.get("address") or "<MISSING>"
        state = x.get("prov") or "<MISSING>"
        country_code = "CN"
        city = x.get("city") or "<MISSING>"
        store_number = x.get("id") or "<MISSING>"
        pos = str(x.get("position")) or "<MISSING>"
        try:
            latitude = pos.split(",")[1].strip()
            longitude = pos.split(",")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = x.get("tel") or "<MISSING>"
        if "暂无" in phone or "无" in phone:
            phone = "<MISSING>"
        hours_of_operation = (
            str(x.get("opentime"))
            .replace("\r\n", " ")
            .replace("\xa0", "")
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("<") != -1:
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
        if "暂无" in hours_of_operation:
            hours_of_operation = "<MISSING>"
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("&nbsp;", "").strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
