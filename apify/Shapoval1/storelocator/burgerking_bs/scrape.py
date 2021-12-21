from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.burgerking.bs/"
    for i in range(0, 100):
        page_url = f"http://www.burgerking.bs/locations?field_geofield_distance%5Borigin%5D%5Blat%5D=25.066667&field_geofield_distance%5Borigin%5D%5Blon%5D=-77.333333&page={i}&target=Nassau"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="bk-restaurants"]/ul/li')
        if len(div) == 0:
            return
        for d in div:

            street_address = (
                "".join(d.xpath('.//div[@class="bk-address1"]/text()')) or "<MISSING>"
            )
            postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()')) or "<MISSING>"
            country_code = (
                "".join(d.xpath('.//div[@class="bk-country"]/text()')) or "<MISSING>"
            )
            city = "".join(d.xpath('.//div[@class="bk-city"]/text()')) or "<MISSING>"
            store_number = (
                "".join(d.xpath('.//div[@class="bk-counter"]/text()')) or "<MISSING>"
            )
            latitude = (
                "".join(d.xpath('.//div[@class="bk-latitude"]/text()')) or "<MISSING>"
            )
            longitude = (
                "".join(d.xpath('.//div[@class="bk-longitude"]/text()')) or "<MISSING>"
            )
            phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()')) or "<MISSING>"
            hours_of_operation = (
                "".join(d.xpath('.//div[@class="bk-weekday-hours"]//text()'))
                + "".join(d.xpath('.//div[@class="bk-weekend-hours"]/text()'))
                or "<MISSING>"
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=SgRecord.MISSING,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
