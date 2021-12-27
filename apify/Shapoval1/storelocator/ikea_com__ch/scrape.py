import json
from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com/ch/en/"
    api_url = (
        "https://www.ikea.com/ch/de/data-sources/93cccdb0b97f11eba11059581bd0eafb.json"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["locations"].values()
    for j in js:

        page_url = j.get("url")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        if location_name == "Click & Collect":
            continue
        ad = tree.xpath('//p[./a[contains(@href, "maps")]]//text()')
        adr = " ".join(ad[1:]).strip()
        if len(ad) > 3:
            adr = " ".join(ad[2:]).strip()
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        country_code = "CH"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if page_url == "https://www.ikea.com/ch/fr/stores/aubonne/":
            street_address = "Pré-Neuf"
            postal = "1170"
            city = "Aubonne"
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

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[text()="Einrichtungshaus"]/following-sibling::text() | //p[./strong[text()="Horaires Restaurant"]]/preceding-sibling::p/text() | //h3[text()="Öffnungszeiten"]/following-sibling::p/text()'
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
                        '//h3[text()="Horaires d’ouverture"]/following-sibling::p/text()'
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
                        '//h3[text()="Orari d’apertura"]/following-sibling::p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Aperto Aperto") != -1:
            hours_of_operation = hours_of_operation.split("Aperto Aperto")[0].strip()
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        '//p[./strong[text()="Öffnungszeiten "]]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if street_address == "<MISSING>":
            js = "".join(
                tree.xpath('//script[contains(text(), "streetAddress")]/text()')
            )
            j = json.loads(js)
            street_address = j.get("address").get("streetAddress")
            city = j.get("address").get("addressLocality")
            postal = j.get("address").get("postalCode")
            latitude = j.get("geo").get("latitude")
            longitude = j.get("geo").get("longitude")
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[contains(text(), "Öffnungszeiten:")]/text()[position() > 1]'
                    )
                )
                .replace("\n", "")
                .strip()
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

    locator_domain = "https://www.ikea.com/at/de/"
    api_url = "https://www.ikea.com/at/de/data-sources/a29ea100ac3111e88ff9755cffc57024.json?1630929072875"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["pois"]
    for j in js:

        page_url = j.get("url")
        location_name = j.get("title")
        location_type = j.get("type")
        if location_type != "store":
            continue
        ad = "".join(j.get("address"))
        street_address = ad.split(",")[0].strip()
        if ad.count(",") > 1:
            street_address = " ".join(ad.split(",")[:2])
        country_code = "AT"
        postal = ad.split(",")[-1].split()[0].strip()
        city = " ".join(ad.split(",")[-1].split()[1:])
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = " ".join(j.get("openinghours")).replace("\n", "").strip()

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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
