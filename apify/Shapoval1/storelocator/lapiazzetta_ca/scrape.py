from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://lapiazzetta.ca/"
    api_url = "https://lapiazzetta.ca/restaurants/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//article[@data-id]")
    for d in div:

        page_url = "".join(d.xpath("./@data-link"))
        location_name = "".join(d.xpath("./@data-title"))
        street_address = (
            "".join(d.xpath('.//p[@class="address"]/a/text()[1]'))
            .replace(",", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="address"]/a/text()[2]'))
            .replace("\n", "")
            .replace("Saint-Nicolas", "Saint-Nicolas,")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:])
        country_code = "CA"
        city = ad.split(",")[0].strip()
        store_number = "".join(d.xpath("./@data-id"))
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//*[@itemprop="openingHoursSpecification"]/*//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        cms = "".join(
            tree.xpath('//strong[contains(text(), "OUVERTURE MAI 2022")]/text()')
        )
        if cms:
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
