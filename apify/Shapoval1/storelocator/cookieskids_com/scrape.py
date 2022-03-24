import cloudscraper
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cookieskids.com/"
    api_url = "https://www.cookieskids.com/locations.aspx"
    session = SgRequests()
    scraper = cloudscraper.create_scraper(sess=session)
    r = scraper.get(api_url).text

    tree = html.fromstring(r)
    div = tree.xpath('//div[contains(@class, "large-6 column sl-section")]')
    for d in div:

        page_url = "https://www.cookieskids.com/locations.aspx"
        location_name = "".join(d.xpath(".//strong/text()"))
        ad = (
            " ".join(d.xpath('.//div[@class="sl-info"]/div[position()<3]/text()'))
            .replace("\n", "")
            .strip()
        )
        street_address = " ".join(ad.split(",")[0].split()[:-1])
        strslug = " ".join(street_address.split()[1:3])
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        latitude = (
            "".join(
                d.xpath(f'.//following::script[contains(text(), "{strslug}")]/text()')
            )
            .split(f"'{strslug}',")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(f'.//following::script[contains(text(), "{strslug}")]/text()')
            )
            .split(f"'{strslug}',")[1]
            .split(",")[1]
            .split("]")[0]
            .strip()
        )
        phone = (
            "".join(d.xpath('.//div[@class="sl-info"]/div[position()>2]/text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = "".join(
            d.xpath('.//preceding::div[@class="sl-hours-heading"][1]/text()')
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
