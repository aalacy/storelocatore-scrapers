from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cashconverters.fr/"
    api_url = "https://www.franchise.cashconverters.fr/nos-magasins/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3/following-sibling::*//a")

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if (
            page_url.find("maps") != -1
            or page_url.find("google") != -1
            or page_url == "#"
        ):
            continue
        if (
            page_url.find("occasion") != -1
            or page_url.find("franchise.cashconverters") != -1
        ):
            continue
        location_name = "".join(d.xpath(".//text()")).strip()
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            continue
        ad = (
            "".join(
                tree.xpath(
                    '//h3[text()="Coordonnées"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = " ".join(ad.split())
        if ad == "<MISSING>":
            ad = (
                "".join(
                    tree.xpath(
                        '//strong[contains(text(), "Adresse")]/following-sibling::*[1]//text() | //strong[contains(text(), "Adresse")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if ad.find("Labège près") != -1:
            ad = ad.split("Labège près")[0].strip()
        ad = ad.replace("42 000", "42000").strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FR"
        city = a.city or "<MISSING>"
        if postal == "<MISSING>":
            postal = ad.split("- ")[-1].split()[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//h3[text()="Coordonnées"]/following-sibling::div[2]//text()'
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
                        '//strong[contains(text(), "Téléphone")]/following-sibling::*[1]//text() | //strong[contains(text(), "Téléphone")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        phone = phone.replace(".", "").strip()
        phone = " ".join(phone.split())
        _tmp = []
        days = tree.xpath('//table[@class="company_schedules_table"]//tr/th[1]//text()')
        days = list(filter(None, [a.strip() for a in days]))
        times = tree.xpath(
            '//table[@class="company_schedules_table"]//tr/td[1]//text()'
        )
        times = list(filter(None, [a.strip() for a in times]))
        for b, t in zip(days, times):
            _tmp.append(f"{b.strip()}: {t.strip()}")
        hours_of_operation = (
            "; ".join(_tmp).replace("\n", "").replace("\r", "").strip() or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//td[./img[contains(@src, "horaire")]]/following-sibling::td[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
