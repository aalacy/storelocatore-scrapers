from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.armstronggarden.com"
    api_url = "https://www.armstronggarden.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-item"]')
    for d in div:
        slug = "".join(d.xpath('.//a[text()="Store Details"]/@href'))
        page_url = f"https://www.armstronggarden.com{slug}"
        location_name = "".join(d.xpath('.//h3[@class="location-title"]/text()'))
        street_address = "".join(
            d.xpath('.//div[@class="location-address"]/div[1]/text()')
        )
        ad = (
            "".join(d.xpath('.//div[@class="location-address"]/div[2]/text()'))
            .replace("\r\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(tree.xpath(".//div/@data-locations"))
            .split(f"{location_name}")[1]
            .split('"position":["')[1]
            .split('",')[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath(".//div/@data-locations"))
            .split(f"{location_name}")[1]
            .split('"position":["')[1]
            .split('","')[1]
            .split('"')[0]
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = "".join(d.xpath('.//div[@class="hours-line"]/text()'))

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
