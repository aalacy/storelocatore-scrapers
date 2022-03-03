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
        locator_domain = "https://gnclivewell.com.hk"
        page_url = "https://gnclivewell.com.hk/store-location/?lang=en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=page_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="all-store-list"]/div[./div]')
        for d in div:

            location_name = (
                "".join(d.xpath('./div[@class="vc_col-sm-2"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            ad = (
                "".join(d.xpath('./div[@class="vc_col-sm-6"]//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            info = "".join(d.xpath('.//div[@class="vc_col-sm-3"]/img/@src'))
            location_type = "<MISSING>"
            if "gnc-store-logo" in info:
                location_type = "GNC Store"
            if "mannings-logo" in info:
                location_type = "Mannings Store"
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            country_code = "HK"
            city = location_name.replace("International Airport", "").strip()
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
