from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bhotelsandresorts.com/"
    api_url = "https://www.bhotelsandresorts.com/destinations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="LEARN MORE"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//preceding-sibling::h2[1]/text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(tree.xpath('//p[text()="Main"]/preceding-sibling::p[1]/text()[1]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//p[text()="Main"]/preceding-sibling::p[1]/text()[2]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        state = ad.split()[-2].strip()
        postal = ad.split()[-1].strip()
        country_code = "US"
        city = " ".join(ad.split()[:-2]).strip()
        phone = (
            "".join(tree.xpath('//p[text()="Main"]/following-sibling::p[1]/text()'))
            .replace("\n", "")
            .replace(",", "")
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
