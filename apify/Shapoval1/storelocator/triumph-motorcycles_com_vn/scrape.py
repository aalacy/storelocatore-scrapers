import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://www.triumph-motorcycles.com.vn/"
        api_url = "https://www.triumph-motorcycles.com.vn/tim-dai-ly"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="cols__inner"]')
        for d in div:

            page_url = "https://www.triumph-motorcycles.com.vn/tim-dai-ly"
            location_name = "".join(
                d.xpath('.//div[@class="form_lienhe__tt"]/span/text()')
            )
            ad = (
                "".join(d.xpath('.//div[@class="form_lienhe__tt"]/span/@data-address'))
                .replace("<br>", " ")
                .strip()
                or "<MISSING>"
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "VN"
            city = a.city or "<MISSING>"
            latitude = (
                "".join(d.xpath('.//div[@class="form_lienhe__tt"]/span/@data-lat'))
                or "<MISSING>"
            )
            longitude = (
                "".join(d.xpath('.//div[@class="form_lienhe__tt"]/span/@data-long'))
                or "<MISSING>"
            )
            phone = (
                "".join(d.xpath('.//div[@class="form_lienhe__tt"]/span/@data-phone'))
                .replace("Cửa hàng:", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find("<br>") != -1:
                phone = phone.split("<br>")[0].strip()
            if phone.find("B") != -1:
                phone = phone.split("B")[0].strip()
            hours_of_operation = (
                "".join(d.xpath('.//div[@class="form_lienhe__tt"]/span/@data-des'))
                or "<MISSING>"
            )
            if hours_of_operation.find("<br/>") != -1:
                hours_of_operation = (
                    hours_of_operation.split("<br/>")[0].replace("/", "").strip()
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
