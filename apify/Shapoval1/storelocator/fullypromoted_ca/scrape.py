from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fullypromoted.ca/"
    api_url = "https://fullypromoted.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-6"]/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://fullypromoted.ca{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//div[@class="pt-2 pb-4 px-4"]/h4[1]/text()'))
            or "<MISSING>"
        )
        street_address = (
            "".join(
                tree.xpath(
                    '//div[@class="pt-2 pb-4 px-4"]/h4[1]/following::p[1]/span/text()'
                )
            )
            or "<MISSING>"
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="pt-2 pb-4 px-4"]/h4[1]/following::p[1]/text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(
                tree.xpath('//script[contains(text(), "ProfessionalService")]/text()')
            )
            .split('"latitude":')[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath('//script[contains(text(), "ProfessionalService")]/text()')
            )
            .split('"longitude":')[1]
            .split("}")[0]
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="pt-2 pb-4 px-4"]//a[contains(@href, "tel")]/text()'
                )
            )
            .replace("Call us:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath("//table//tr/td/text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
