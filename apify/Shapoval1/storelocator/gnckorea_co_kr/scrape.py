from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.gnckorea.co.kr/"
    page_url = "https://www.gnckorea.co.kr/services/Store/StoreInfo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    data = {"pageno": "1", "location1": "", "sellerName": "", "shopName": ""}
    r = session.post(page_url, headers=headers, data=data)

    tree = html.fromstring(r.text)
    last = (
        "".join(tree.xpath('.//div[@class="board_pager"]//a[text()="last"]/@href'))
        .split("(")[1]
        .split(")")[0]
        .strip()
    )
    for i in range(1, int(last) + 1):
        data = {"pageno": f"{i}", "location1": "", "sellerName": "", "shopName": ""}
        session = SgRequests()
        r = session.post(page_url, headers=headers, data=data)
        tree = html.fromstring(r.text)
        div = tree.xpath('//ul[@class="storeList"]/li/div[@class="storeBox"]')
        for d in div:

            location_name = (
                "".join(d.xpath(".//h2/text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
            ad = "".join(d.xpath('.//p[@class="addr"]/text()'))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "KR"
            city = a.city or "<MISSING>"
            latitude = (
                "".join(d.xpath('.//a[@class="btn_mapView"]/@onclick'))
                .split("(")[1]
                .split(",")[0]
                .replace("'", "")
                .strip()
            )
            longitude = (
                "".join(d.xpath('.//a[@class="btn_mapView"]/@onclick'))
                .split("(")[1]
                .split(",")[1]
                .replace("'", "")
                .strip()
            )
            phone = "".join(d.xpath('.//p[@class="tel"]/text()')) or "<MISSING>"
            hours_of_operation = (
                "".join(d.xpath('.//p[@class="time"]//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
