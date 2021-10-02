from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.com.py/"
    for i in range(0, 100):
        page_url = f"https://www.burgerking.com.py/locations?field_geofield_distance%5Borigin%5D%5Blat%5D=-25.263716&field_geofield_distance%5Borigin%5D%5Blon%5D=-57.57596&target=Asuncion&page={i}"
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

            street_address = "".join(d.xpath('.//div[@class="bk-address1"]/text()'))
            postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
            country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
            city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
            store_number = "".join(d.xpath('.//div[@class="bk-counter"]/text()'))
            latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
            longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
            phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
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
