from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cannacabana.com"
    api_url = "https://cannacabana.com/a/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "col-4_xs-12 storeLocation")]')
    for d in div:

        slug = "".join(d.xpath('.//a[contains(text(), "View Details")]/@href'))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath("./h3//text()"))
        street_address = (
            "".join(
                d.xpath(
                    './/i[@class="bi bi-geo-alt-fill"]/following-sibling::div[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './/i[@class="bi bi-geo-alt-fill"]/following-sibling::div[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip() or "<MISSING>"
        postal = (
            " ".join(ad.split(",")[1].split()[1:]).replace("ON", "").strip()
            or "<MISSING>"
        )
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = ad.split(",")[0].strip() or "<MISSING>"
        if street_address.find("Regina") != -1:
            street_address = street_address.split(f"{city}")[0].replace(",", "").strip()
        cont = (
            "".join(
                d.xpath(
                    './/i[@class="bi bi-briefcase-fill"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        store_number = "<MISSING>"
        if cont.find("#") != -1:
            store_number = cont.split("#")[1].strip()
        if not store_number.isdigit():
            store_number = "<MISSING>"
        ll = "".join(d.xpath('.//a[contains(text(), "Get Directions")]/@href'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll.find("destination") != -1:
            latitude = ll.split("destination=")[1].split(",")[0].strip()
            longitude = ll.split("destination=")[1].split(",")[1].strip()
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    './/i[@class="bi bi-telephone-fill"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/i[@class="bi bi-clock-fill"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace(",", "").strip()
        )
        if hours_of_operation.find("Temporary Hours") != -1:
            hours_of_operation = hours_of_operation.split("Temporary Hours")[0].strip()

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
