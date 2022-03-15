from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    if tree.xpath("//span[contains(text(), 'TEMPORARILY')]"):
        return "TEMPORARILY CLOSED"

    _tmp = []
    days = tree.xpath("//tbody[@class='row-hover']/tr[1]/td/text()")
    days = list(filter(None, [d.strip() for d in days]))
    tr = tree.xpath("//tbody[@class='row-hover']/tr")
    tr.pop(0)
    for t in tr:
        name = "".join(t.xpath("./td[1]/text()")).strip()
        td = t.xpath("./td")
        td.pop(0)
        lines = []
        for day, inter in zip(days, td):
            lines.append(f'{day}: {"".join(inter.xpath("./text()"))}'.strip())
        _tmp.append(f'{name}: {";".join(lines)}')

    return " | ".join(_tmp)


def fetch_data(sgw: SgWriter):
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    urls = dict()
    blocks = tree.xpath(
        "//div[contains(@class, 'elementor-column elementor-col-33') and .//h3 and .//a]"
    )
    for b in blocks:
        key = "".join(b.xpath(".//h3/text()")).strip()
        url = "".join(b.xpath(".//a/@href"))
        urls[key] = url

    divs = tree.xpath(
        "//div[contains(@class, 'elementor-column elementor-col-33') and .//h4 and .//a]"
    )
    for d in divs:
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        page_url = urls.get(location_name)
        line = d.xpath(".//p/text()")
        line = list(filter(None, [l.replace("\xa0", " ").strip() for l in line]))
        street_address = line.pop(0)
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        city, postal = line.pop().split(", ")
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]//text()")).strip()
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.wingwah.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
