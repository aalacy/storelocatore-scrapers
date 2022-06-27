from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://foxetcompagnie.be/"
    api_url = "https://foxetcompagnie.be/fr/magasins"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "magasin-list")]')
    for d in div:

        page_url = "".join(d.xpath(".//a/@href"))
        store_number = page_url.split("=")[-1].strip()
        location_name = "".join(d.xpath(".//h2//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(
                tree.xpath('//h2[text()="Adresse"]/following-sibling::p[1]/text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath('//h2[text()="Adresse"]/following-sibling::p[1]/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        postal = ad.split()[0].strip()
        country_code = "BE"
        city = " ".join(ad.split()[1:]).strip()
        ll = "".join(tree.xpath("//iframe/@src"))
        latitude = ll.split("q=")[-1].split(",")[0].strip()
        longitude = ll.split("q=")[-1].split(",")[1].split("&")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//h2[text()="Contactez-nous"]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(tree.xpath('//h2[text()="Horaires"]/following-sibling::p//text()'))
            .replace("\n", "")
            .replace("Voir sélection produit", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
