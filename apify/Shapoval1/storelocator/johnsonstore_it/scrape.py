from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.johnsonstore.it/stores/"
    api_url = "https://www.johnsonstore.it/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="button white is-outline expand"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        city = "".join(d.xpath(".//span/text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = (
            " ".join(tree.xpath("//h1/following-sibling::p[1]//text()"))
            .replace("\n", "")
            .strip()
        )
        if ad.find("Tel") != -1:
            ad = ad.split("Tel")[0].strip()
        if ad.find("Aperto") != -1:
            ad = ad.split("Aperto")[0].strip()
        if ad.find("Orari") != -1:
            ad = ad.split("Orari")[0].strip()
        if ad.find("Dal") != -1:
            ad = ad.split("Dal")[0].strip()

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = a.postcode or "<MISSING>"
        country_code = "IT"
        map_link = "".join(tree.xpath("//iframe/@suppressedsrc"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            map_link = "".join(tree.xpath("//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/@href'))
            .replace("tel:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath("//h1/following-sibling::p//text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.split(f"{ad}")[1].strip()
        if hours_of_operation.find("APERTURE") != -1:
            hours_of_operation = hours_of_operation.split("APERTURE")[0].strip()
        if hours_of_operation.find("Tel") != -1:
            hours_of_operation = hours_of_operation.split("Tel")[0].strip()
        if hours_of_operation.find("24 e 31") != -1:
            hours_of_operation = hours_of_operation.split("24 e 31")[0].strip()
        if hours_of_operation == "Aperto solo su appuntamento":
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
