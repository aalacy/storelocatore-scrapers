from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.buchbinder.de/"
    api_url = "https://www.buchbinder.de/de/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//loc[contains(text(), "station")]')
    for d in div:
        station_sitemap = "".join(d.xpath(".//text()"))
        r = session.get(station_sitemap, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath("//loc")
        for d in div:

            page_url = "".join(d.xpath(".//text()"))
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = (
                "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
            )
            street_address = (
                "".join(tree.xpath("//address/p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(tree.xpath("//address/p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
            postal = ad.split()[0].strip()
            country_code = "DE"
            city = " ".join(ad.split()[1:]).strip()
            if city.find("/") != -1:
                city = city.split("/")[0].strip()
            ll = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
            try:
                latitude = ll.split("=")[-1].split(",")[0].strip()
                longitude = ll.split("=")[-1].split(",")[1].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(
                    tree.xpath(
                        '//p[@class="station-details__icon station-details__icon--phone"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(tree.xpath("//dl/*/text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    "".join(tree.xpath("//dl/text()")).replace("\n", "").strip()
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
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)

    locator_domain = "https://www.buchbinder.de/"
    api_url = "https://at.buchbinder.de/at/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//loc[contains(text(), "station")]')
    for d in div:
        station_sitemap = "".join(d.xpath(".//text()"))
        r = session.get(station_sitemap, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath("//loc")
        for d in div:

            page_url = "".join(d.xpath(".//text()"))
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = (
                "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
            )
            street_address = (
                "".join(tree.xpath("//address/p[1]/text()[1]"))
                .replace("Car Rental Pavillon", "")
                .replace("/Arrival Hall", "")
                .replace("Parkhaus / Parking House", "")
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(tree.xpath("//address/p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
            postal = ad.split()[0].strip()
            country_code = "AT"
            city = " ".join(ad.split()[1:]).strip()
            if city.find("/") != -1:
                city = city.split("/")[0].strip()
            ll = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
            try:
                latitude = ll.split("=")[-1].split(",")[0].strip()
                longitude = ll.split("=")[-1].split(",")[1].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(
                    tree.xpath(
                        '//p[@class="station-details__icon station-details__icon--phone"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(tree.xpath("//dl/*/text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    "".join(tree.xpath("//dl/text()")).replace("\n", "").strip()
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
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
