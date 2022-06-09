from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://moomoocarwash.com/"
    api_url = "https://moomoocarwash.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="popup_detail_content"]')
    for d in div:

        page_url = "https://moomoocarwash.com/locations/"
        location_name = "".join(d.xpath(".//h3/text()")) or "<MISSING>"
        street_address = (
            "".join(d.xpath('.//div[@class="location-address"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//div[@class="location-address"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        adr = (
            "".join(d.xpath('.//div[@class="location-address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        adr = " ".join(adr.split())
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        latitude = (
            "".join(
                d.xpath(
                    f'.//following::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[0]
            .split("lat:")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    f'.//following::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[0]
            .split("lng:")[-1]
            .split("}")[0]
            .strip()
        )
        hours_of_operation = (
            "".join(d.xpath('.//preceding::span[contains(text(), "Hours:")][1]/text()'))
            .replace("Hours:", "")
            .strip()
        )
        cms = "".join(d.xpath(".//img/@src"))
        if "coming-soon" in cms:
            hours_of_operation = "Coming Soon"

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
