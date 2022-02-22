from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    page_url = "https://www.crutchfield.com/Crutchfield-Stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-12 col-sm-4 card contact-desktop"]/h4')
    for d in div:
        location_name = "".join(d.xpath(".//text()"))
        street_address = "".join(
            d.xpath(
                './/following-sibling::div[@class="location row"][1]/div[@class="col address"]/a/text()[1]'
            )
        )
        ad = (
            "".join(
                d.xpath(
                    './/following-sibling::div[@class="location row"][1]/div[@class="col address"]/a/text()[2]'
                )
            )
            .replace("\n", "")
            .replace("US", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        text = "".join(
            d.xpath(
                './/following-sibling::div[@class="location row"][1]/div[@class="col address"]/a/@href'
            )
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
        phone = (
            "".join(
                d.xpath(
                    './/following-sibling::div[@class="location row"][1]/div[@class="col phone"]/a/div/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following-sibling::h5[contains(text(), "Hours")][1]/following-sibling::table[1]//tr/td//text()'
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.crutchfield.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
