from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.burgerking.com.hn/"
    for i in range(0, 100):
        page_url = f"http://www.burgerking.com.hn/locations?field_geofield_distance%5Borigin%5D%5Blat%5D=14.072264&field_geofield_distance%5Borigin%5D%5Blon%5D=-87.192147&page={i}&target=Tegucigalpa"
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
                "".join(d.xpath('.//div[@class="bk-address1"]/text()'))
                .replace(", TEGUCIGALPA", "")
                .strip()
            )
            state = "".join(d.xpath('.//div[@class="bk-province-name"]/text()'))
            postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
            country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
            city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
            store_number = "".join(d.xpath('.//div[@class="bk-counter"]/text()'))
            latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
            longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
            phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
            if phone == "0":
                phone = "<MISSING>"
            hours_of_operation = (
                "Weekday "
                + "".join(d.xpath('.//div[@class="bk-weekday-hours"]//text()'))
                + " "
                + "Weekend "
                + "".join(d.xpath('.//div[@class="bk-weekend-hours"]/text()'))
                or "<MISSING>"
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=SgRecord.MISSING,
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
