from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com/fr/"
    api_url = "https://www.ikea.com/fr/fr/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//p[./a]")
    for d in div:
        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//p/strong[contains(text(), "IKEA ")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad.find(", vous serez aussi") != -1:
            ad = ad.split(", vous serez aussi")[0].strip()
        if ad.find("Vous serez aussi") != -1:
            ad = ad.split("Vous serez aussi")[0].strip()
        if ad.find("à la conception pour tous vos projets !") != -1:
            ad = ad.split("à la conception pour tous vos projets !")[1].strip()

        if page_url == "https://www.ikea.com/fr/fr/stores/grand-parilly/":
            ad = (
                " ".join(
                    tree.xpath('//p[./strong[contains(text(), "IKEA Grand")]]/text()')
                )
                .replace("\n", "")
                .strip()
            )
        if page_url.find("marseille-la-valentine") != -1:
            ad = (
                " ".join(
                    tree.xpath(
                        '//p/strong[contains(text(), "Marseille - La Valentine")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if page_url == "https://www.ikea.com/fr/fr/stores/paris-la-madeleine/":
            ad = (
                " ".join(
                    tree.xpath(
                        '//p/strong[contains(text(), "City Paris La Madeleine")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )

        location_name = "".join(tree.xpath("//h1/text()")).strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FR"
        city = a.city or "<MISSING>"
        if street_address == "2 Montpellier Cedex":
            street_address = "Zone Odysséum 1 place de Troie"
            city = "Montpellier"
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href')) or "<MISSING>"
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            try:
                latitude = text.split("!3d")[1].split("!")[0].strip()
                longitude = text.split("!4d")[1].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Horaires d\'ouverture")]]/text()'
                )
            ).replace("\n", "")
            or "<MISSING>"
        )
        if page_url == "https://www.ikea.com/fr/fr/stores/rennes/":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//p[./strong[contains(text(), "Magasin ")]]/text()')
                ).replace("\n", "")
                or "<MISSING>"
            )
        if page_url == "https://www.ikea.com/fr/fr/stores/grand-parilly/":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Horaires d\'ouverture")]]/following-sibling::p[1]/text()'
                    )
                ).replace("\n", "")
                or "<MISSING>"
            )
        if page_url == "https://www.ikea.com/fr/fr/stores/bordeaux/":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Magasin")]]/following-sibling::p[1]/text()'
                    )
                ).replace("\n", "")
                or "<MISSING>"
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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
