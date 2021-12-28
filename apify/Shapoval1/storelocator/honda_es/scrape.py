from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.es/"
    api_url = "https://www.honda.es/cars/concesionarios.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//table//tr/td/a")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.honda.es{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()"))
        street_address = (
            "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        street_address = " ".join(street_address.split())
        postal = (
            "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "ES"
        city = (
            "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        text = "".join(tree.xpath('//div[@class="dealer-map"]/a/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//section[.//h1]/following-sibling::section[1]//a[contains(@href, "tel")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//section[.//h1]/following-sibling::section[2]//a[contains(@href, "tel")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {city} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
