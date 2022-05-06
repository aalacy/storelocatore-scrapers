from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nahundfrisch.de"
    api_url = "https://www.nahundfrisch.de/karte/index.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[contains(text(), "var point")]/text()')).split(
        "var point"
    )
    for d in div[1:]:

        block = d.split('","')[1].split('"')[0].strip()
        tree = html.fromstring(block)
        ad = tree.xpath("//p//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = "".join(ad[0]).replace("\\", "").replace("/", "").strip()
        adr = " ".join(adr.split())
        slug = (
            "".join(tree.xpath("//a/@href")).replace("\\", "").replace("..", "").strip()
        )
        page_url = f"{locator_domain}{slug}"
        location_name = (
            d.split('point,"')[1]
            .split('"')[0]
            .replace("<br>", " ")
            .replace("&amp;", "&")
            .strip()
        )
        street_address = "".join(ad[1]).replace("\\", " ").replace("/", " ").strip()
        street_address = " ".join(street_address.split())
        postal = adr.split()[0].strip()
        country_code = "DE"
        city = " ".join(adr.split()[1:]).strip()
        store_number = slug.split("=")[-1].strip()
        latitude = d.split("LatLng(")[1].split(",")[0].strip()
        longitude = d.split("LatLng(")[1].split(",")[1].split(")")[0].strip()
        phone_check = "".join(ad[2]).replace("-", "").replace(" ", "").strip()
        phone = "<MISSING>"
        if phone_check.isdigit():
            phone = "".join(ad[2]).strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h1[text()="Öffnungszeiten:"]/following-sibling::table//tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("Saison") != -1:
            hours_of_operation = hours_of_operation.split("Saison")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {adr}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
