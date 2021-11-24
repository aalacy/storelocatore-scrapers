from sgrequests import SgRequests
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_coords(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))

    try:
        lat = text.split("@")[1].split(",")[0]
        lng = text.split("@")[1].split(",")[1]
    except:
        lat, lng = SgRecord.MISSING, SgRecord.MISSING

    return lat, lng


def get_data(page_url, sgw):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='wysiwyg__p']/text()")).strip()
    line = tree.xpath(
        "//span[contains(text(), 'Hours')]/a[not(contains(@href, 'tel:'))]/text()"
    )
    line = list(filter(None, [l.replace("Address:", "").strip() for l in line]))
    if not line:
        return

    street_address = line.pop(0)
    city = line.pop(0)
    state = SgRecord.MISSING
    postal = SgRecord.MISSING
    country_code = "US"
    phone = "".join(
        tree.xpath(
            "//span[contains(text(), 'Hours')]/a[contains(@href, 'tel:')]/text()"
        )
    ).strip()

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude = text.split("@")[1].split(",")[0]
    longitude = text.split("@")[1].split(",")[1]

    hours = tree.xpath("//a[contains(@href, 'tel:')]/preceding-sibling::text()")
    hours = list(
        filter(
            None, [h.replace("Hours:", "").replace("Call:", "").strip() for h in hours]
        )
    )
    hours_of_operation = ";".join(hours)

    row = SgRecord(
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
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    api = "https://www.thereformation.com/pages/stores"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    blocks = tree.xpath("//a[@class='image-new-content-block__content-link']/@href")

    for b in blocks:
        if b.startswith("/"):
            continue

        d = tree.xpath(f"//div[@class='store-summary' and .//a[@href='{b}']]")
        if d:
            d = d.pop()
            location_name = "".join(
                d.xpath(".//span[@itemprop='location']/text()")
            ).strip()
            page_url = "".join(d.xpath(".//a[@class='store-summary__image']/@href"))

            line = d.xpath(".//div[@class='store-summary__street']/text()")
            line = list(filter(None, [l.strip() for l in line]))
            street_address = ", ".join(line[:-1])
            line = line[-1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.replace(state, "").strip()
            country_code = "US"

            if city == "North York":
                country_code = "CA"
            if city == "London":
                country_code = "GB"
                state = SgRecord.MISSING

            phone = "".join(d.xpath(".//span[@itemprop='telephone']/a/text()")).strip()
            latitude, longitude = get_coords(page_url)

            hours = d.xpath(".//div[@class='store-summary__text']/text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours)

            row = SgRecord(
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
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)
        else:
            get_data(b, sgw)


if __name__ == "__main__":
    locator_domain = "https://www.thereformation.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
