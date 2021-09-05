from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


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

        location_name = "".join(tree.xpath("//h1/text()")).strip()
        ad = (
            " ".join(
                tree.xpath(
                    '//a[contains(@href, "maps")]/preceding::strong[1]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .replace("Entrée :", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        '//strong[contains(text(), "IKEA Nice")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FR"
        city = a.city or "<MISSING>"
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
        info = (
            tree.xpath(
                '//article/section[.//strong[contains(text(), "IKEA ")]]//text()'
            )
            or "<MISSING>"
        )
        if info == "<MISSING>":
            info = (
                tree.xpath(
                    '//article/section[.//strong[contains(text(), "City Paris La Madeleine")]]//text()'
                )
                or "<MISSING>"
            )
        if info == "<MISSING>":
            info = (
                tree.xpath(
                    '//article/section[.//strong[contains(text(), "Marseille - La Valentine")]]//text()'
                )
                or "<MISSING>"
            )

        tmp = []
        for i in info:
            if i.find("Lun") != -1:
                tmp.append(i)
                break
        hours_of_operation = "".join(tmp)

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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
