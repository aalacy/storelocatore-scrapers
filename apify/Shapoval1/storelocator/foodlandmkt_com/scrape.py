from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://foodlandmkt.com"
    api_url = "https://foodlandmkt.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-data"]')

    for d in div:
        slug = "".join(d.xpath('.//h3[@class="site-loc-name"]/a/@href'))
        page_url = f"{locator_domain}{slug}"
        title = (
            "".join(d.xpath('.//h3[@class="site-loc-name"]/a/text()'))
            .replace("\n", "")
            .strip()
        )
        street_address = "".join(d.xpath('.//div[@class="site-loc-address"]/text()'))
        ad = "".join(d.xpath('.//div[@class="site-city-state-zip"]/text()'))
        phone = (
            "".join(d.xpath('.//div[@class="site-loc-phone"]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        location_name = title.split("-")[0].strip()
        store_number = slug.split("+")[-1].strip()
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lon"))
        hours_of_operation = (
            "".join(d.xpath('.//div[@class="site-loc-hours"]/text()'))
            .replace("Hours:", "")
            .strip()
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
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
