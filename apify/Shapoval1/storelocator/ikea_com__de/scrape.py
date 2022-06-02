from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com/de/"
    api_url = "https://www.ikea.com/de/de/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="pub__link-list__item"] | //async-include')
    for d in div:
        slug = "<MISSING>"
        page_url = "".join(d.xpath("./@href")) or "<MISSING>"
        if page_url == "<MISSING>":
            slug = "".join(d.xpath(".//@src"))
        if slug.find("link-list") != -1:
            slug = slug.split("link-list")[0].strip()
        if page_url.find("http") == -1:
            page_url = f"https://www.ikea.com{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = (
            " ".join(
                tree.xpath("//h2[text()='Adresse']/following-sibling::p[1]/text()")
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//h3[contains(text(), "Dein Weg zu uns")]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .replace("IKEA Bestell- und Abholstation Ravensburg", "")
                .replace("IKEA Abholstation Leipzig", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        country_code = "DE"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if page_url == "https://www.ikea.com/de/de/stores/brinkum/":
            street_address = "Henleinstr. 1a"
            city = "Brinkum"
            postal = "28816"
        if page_url == "https://www.ikea.com/de/de/stores/saarlouis/":
            city = "Saarlouis"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Einrichtungshaus"]/following-sibling::div/div/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[./strong[contains(text(), "Öffnungszeiten")]]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h2[text()="Öffnungszeiten"]/following-sibling::div[1]/div[1]//div[@class="openinghours-line"]//text()'
                    )
                )
                or "<MISSING>"
            )
        hours_of_operation = " ".join(hours_of_operation.split())
        if location_name.find(".") != -1:
            location_name = location_name.split(".")[0].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
