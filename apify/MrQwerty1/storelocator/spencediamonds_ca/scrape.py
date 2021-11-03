from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_coords(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    lat = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    lng = "".join(tree.xpath("//div[@data-lng]/@data-lng"))

    return lat, lng


def fetch_data(sgw: SgWriter):
    api = "https://spencediamonds.com/find-a-store/"

    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store-list']")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/a/text()")).strip()
        page_url = "".join(d.xpath(".//h2/a/@href"))

        line = d.xpath(".//div[@class='address']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-2])
        postal = line.pop()
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        country_code = "CA"
        phone = d.xpath(".//a[contains(@href, 'tel:')]/text()")[0].strip()
        latitude, longitude = get_coords(page_url)

        _tmp = []
        li = d.xpath(".//div[@class='hours']/p/text()")
        for l in li:
            if not l.strip():
                continue

            hours = " ".join(l.split())
            _tmp.append(f"{hours}")

        hours_of_operation = ";".join(_tmp)
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
    locator_domain = "https://spencediamonds.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
