from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ironcactus.com/"
    api_url = "https://ironcactus.com/page-sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "locations")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") != 5:
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(tree.xpath('//h2[.//a[contains(@href, "tel")]]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//h2[.//a[contains(@href, "tel")]]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "marker_latitude")]/text()'))
            .split("marker_latitude")[1]
            .split('",')[0]
            .replace('"', "")
            .replace("\\", "")
            .replace(":", "")
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "marker_latitude")]/text()'))
            .split("marker_longitude")[1]
            .split('",')[0]
            .replace('"', "")
            .replace("\\", "")
            .replace(":", "")
            .strip()
        )
        location_name = (
            "".join(tree.xpath('//script[contains(text(), "marker_latitude")]/text()'))
            .split("title")[1]
            .split('",')[0]
            .replace('"', "")
            .replace("\\", "")
            .replace(":", "")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//h2[.//a[contains(@href, "tel")]]/a//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="ic-schedule"]/div/div//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
