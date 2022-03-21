from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kennedyfitness.org/"
    api_url = "https://kennedyfitness.org/page-sitemap.xml"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "locations/")]')

    for d in div:
        page_url = "".join(d.xpath(".//text()"))
        if page_url == "https://kennedyfitness.org/locations/":
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//a[.//span[text()="GIVE US A CALL"]]/preceding::h2[1]//text()')
        )
        street_address = "".join(
            tree.xpath('//h2[text()="Address"]/following::p[1]/text()[1]')
        )
        ad = (
            "".join(tree.xpath('//h2[text()="Address"]/following::p[1]/text()[2]'))
            .replace("\n", "")
            .strip()
        )

        phone = (
            "".join(tree.xpath('//a[.//span[text()="GIVE US A CALL"]]/@href'))
            .replace("tel:", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Club Hours")]/following::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Pool Hours") != -1:
            hours_of_operation = hours_of_operation.split("Pool Hours")[0].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
