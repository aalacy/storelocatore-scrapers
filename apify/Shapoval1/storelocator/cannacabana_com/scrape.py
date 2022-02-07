from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cannacabana.com/"
    api_url = "https://cannacabana.com/a/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p/a[text()="View Details "]]')
    for d in div:

        page_url = "".join(d.xpath('.//a[text()="View Details "]/@href'))
        if page_url.find("http") == -1:
            page_url = f"https://cannacabana.com{page_url}"
        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = (
            "".join(d.xpath('.//span[@class="light-tag"]/text()')) or "<MISSING>"
        )
        info = d.xpath(
            './/i[@class="bi bi-geo-alt-fill"]/following-sibling::div[1]/text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).replace("\xa0", " ").strip()

        ad = (
            "".join(
                d.xpath(
                    './/i[@class="bi bi-geo-alt-fill"]/following-sibling::div[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = (
            " ".join(ad.split(",")[1].split()[1:]).replace("ON", "").strip()
            or "<MISSING>"
        )
        if street_address.find(f"{postal}") != -1:
            street_address = street_address.split(",")[0].strip()
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = ad.split(",")[0].strip()
        if page_url.find("georgia") != -1:
            city, state = state, city
        try:
            latitude = (
                "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
                .split("=")[-1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
                .split("=")[-1]
                .split(",")[1]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
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
            "".join(
                d.xpath(
                    './/i[@class="bi bi-clock-fill"]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
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
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
