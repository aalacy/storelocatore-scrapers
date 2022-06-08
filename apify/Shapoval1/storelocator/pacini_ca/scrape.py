from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pacini.com/"
    api_url = "https://pacini.com/en/restaurants/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="wpb_wrapper"]/ul/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://pacini.com{slug}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//span[@class="blanc"]/text() | //h1/text()')
        )
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        city = "<MISSING>"
        ad = (
            " ".join(tree.xpath('//a[@href="#us_map_1"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = ad.replace("(Québec)", ",Québec")
        if ad.count(",") == 1:
            street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
            city = ad.split(",")[0].split()[-1]
            state = ad.split(",")[1].split()[0]
            postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        if ad.count(",") == 2:
            street_address = (
                ad.split(",")[0] + " " + " ".join(ad.split(",")[1].split()[:-1]).strip()
            )
            city = ad.split(",")[1].split()[-1]
            state = ad.split(",")[2].split()[0]
            postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        phone = (
            "".join(
                tree.xpath(
                    '//a[contains(@href, "tel:")]/text() | //div[./i[@class="fas fa-mobile-alt"]]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            phone.replace("RESERVATION", "")
            .replace("ONLINE", "")
            .replace("Online Reservation", "")
            .replace("Online reservation", "")
            .replace("Book online", "")
            .replace("9733450 359-9733", "9733")
            or "<MISSING>"
        )
        country_code = "CA"
        map_link = "".join(tree.xpath('//iframe[@loading="lazy"]/@src'))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./i[@class="far fa-clock"]]/following-sibling::div[1]/div//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        tmpclz = " ".join(tree.xpath('//div[@class="wpb_wrapper"]/p/text()')).replace(
            "\n", ""
        )
        if tmpclz.find("temporarily close") != -1:
            hours_of_operation = "temporarily close"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
