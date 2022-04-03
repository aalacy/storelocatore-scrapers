from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.arcgroup.uk.com/"
    api_url = "https://www.arcgroup.uk.com/#"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@id="locations_content"]/div/div[contains(@class, "location ")]'
    )
    for d in div:

        location_name = "".join(d.xpath(".//h6/text()")).replace("\n", "").strip()
        ad = (
            "".join(d.xpath('.//div[@class="address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[text()="T:"]/following-sibling::text()[1]'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="opening_times"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        slug = (
            "".join(d.xpath('.//a[contains(@href, "mailto")]/@href'))
            .split("mailto:")[1]
            .split("@")[0]
            .strip()
        )
        latitude = r.text.split(f"var {slug}")[1].split("lat:")[1].split(",")[0]
        longitude = r.text.split(f"var {slug}")[1].split("lng:")[1].split("}")[0]
        slug_info = d.xpath(
            f'.//preceding::li[@class="centres"]//ul[1]/li/a[contains(@href, "{slug}.")]/@href'
        )
        page_url = "".join(slug_info[0]).strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
