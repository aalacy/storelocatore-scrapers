from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ngwtoday.com"
    api_url = "https://www.ngwtoday.com/contact-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3/following-sibling::ul/li/a")

    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        block = tree.xpath('//h2[text()="U.S. Cellular"]')
        for b in block:

            location_name = "".join(b.xpath(".//text()"))
            street_address = (
                "".join(
                    b.xpath(
                        './/following-sibling::p[./a[contains(@href, "mailto")]][1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            ad = (
                "".join(
                    b.xpath(
                        './/following-sibling::p[./a[contains(@href, "mailto")]][1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "USA"
            city = ad.split(",")[0].strip()
            text = "".join(
                b.xpath('.//following-sibling::*/a[contains(@href, "maps")]/@href')
            )
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
                latitude = "".join(
                    b.xpath('.//preceding::div[@class="map-marker"]/@data-lat')
                )
                longitude = "".join(
                    b.xpath('.//preceding::div[@class="map-marker"]/@data-lng')
                )
            phone = (
                "".join(
                    b.xpath(
                        './/following-sibling::p[./a[contains(@href, "mailto")]][1]/text()[3]'
                    )
                )
                .replace("\n", "")
                .replace("Phone", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    b.xpath(
                        './/preceding::*[./span[text()="Store Hours:"]][1]/following-sibling::h4//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            if (
                street_address.find("2515 NW Arterial Drive") != -1
                or street_address.find("401 Locust Street") != -1
            ):
                hours_of_operation = (
                    " ".join(
                        b.xpath(
                            './/following::*[./span[text()="Store Hours:"]][1]/following-sibling::h4//text()'
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
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.ngwtoday.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
