from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_coords(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))

    lat = text.split("@")[1].split(",")[0]
    lng = text.split("@")[1].split(",")[1]
    return lat, lng


def fetch_data(sgw: SgWriter):
    api = "https://www.thereformation.com/pages/stores"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store-summary']")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@itemprop='location']/text()")).strip()
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


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.thereformation.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
