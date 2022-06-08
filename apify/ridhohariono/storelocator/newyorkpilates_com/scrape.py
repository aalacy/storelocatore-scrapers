from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.newyorkpilates.com/"
    api_url = "https://www.newyorkpilates.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="ft"]/following-sibling::div[1]//section[.//a]')
    for d in div:

        page_url = "".join(d.xpath(".//a/@href"))
        if page_url.find("http") == -1:
            page_url = f"https://www.newyorkpilates.com/{page_url}/"
        location_name = "".join(d.xpath(".//a/text()"))
        street_address = "".join(d.xpath(".//p/text()[1]")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//p/text()[3]")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[contains(text(), "PM")]//text() | //p[contains(text(), "AM-")]//text()'
                )
            )
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
            phone=SgRecord.MISSING,
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
