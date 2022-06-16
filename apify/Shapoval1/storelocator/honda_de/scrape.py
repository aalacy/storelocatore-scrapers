from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.de/"
    api_urls = [
        "https://www.honda.cz/cars/sitemap.xml",
        "https://www.honda.sk/cars/sitemap.xml",
        "https://www.honda.de/cars/sitemap.xml",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath('//url/loc[contains(text(), "/dealers/")]')
        for d in div:

            page_url = "".join(d.xpath(".//text()"))
            country_code = page_url.split("honda.")[1].split("/")[0].upper().strip()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//h1/text()"))
            store_number = "<MISSING>"
            if page_url.find("dealers/S") != -1:
                store_number = page_url.split("dealers/")[1].split(".")[0].strip()
            location_type = (
                "".join(
                    tree.xpath(
                        '//section[@class="fad-dealer-details"]/following-sibling::section[1]//h2/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            street_address = (
                "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
                .replace("\n", "")
                .replace(",", "")
                .strip()
            )
            state = (
                "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            postal = (
                "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
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
                        '//section[@class="fad-dealer-details"]/following-sibling::section[1]//a[contains(@href, "tel:")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            if phone.find("(") != -1:
                phone = phone.split("(")[0].strip()

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//section[@class="fad-dealer-details"]/following-sibling::section[1]//*[@class="timings"]/*/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city} {postal}".replace(
                    "<MISSING>", ""
                ).strip(),
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
