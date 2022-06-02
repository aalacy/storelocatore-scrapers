from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_coords(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//script[contains(text(), '.LatLng')]/text()"))
    return eval(text.split(".LatLng")[1].split("),")[0] + ")")


def fetch_data(sgw: SgWriter):
    api = "https://www.buckmason.com/pages/our-stores"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store ']")

    for d in divs:
        slug = "".join(d.xpath(".//div[@class='store-title']/a/@href"))
        page_url = api
        if slug:
            page_url = f"https://www.buckmason.com{slug}"

        location_name = "".join(
            d.xpath(
                ".//div[@class='store-title']/a/text()|.//div[@class='store-title']/text()"
            )
        ).strip()

        line = d.xpath(".//div[@class='store-address']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            continue
        street_address = ", ".join(line[:-1]).replace("Westfield, ", "")
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = "".join(
            d.xpath(".//a[@class='store-detail__telephone']/text()")
        ).strip()

        try:
            latitude, longitude = get_coords(page_url)
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        black_list = ["dec", "christmas", "new", "/", "thanksgiving", "xmas"]
        hours = d.xpath(".//div[@class='store-hours']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        for h in hours:
            if "holiday" in h.lower():
                break
            for b in black_list:
                if b in h.lower():
                    break
            else:
                _tmp.append(h)

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
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.buckmason.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
