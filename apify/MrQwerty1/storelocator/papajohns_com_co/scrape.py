from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_initial():
    ids = dict()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    options = tree.xpath(
        "//select[@name='ctl00$ContentPlaceHolder1$ddlCiudades']/option"
    )
    for op in options:
        _id = "".join(op.xpath("./@value"))
        city = "".join(op.xpath("./text()")).strip()
        ids[_id] = city
    view = "".join(tree.xpath("//input[@id='__VIEWSTATE']/@value"))
    token = r.cookies.get("__AntiXsrfToken")

    return token, view, ids


def fetch_data(sgw: SgWriter):
    token, view, ids = get_initial()
    cookies = {"__AntiXsrfToken": token}

    for _id, city in ids.items():
        data = {
            "__VIEWSTATE": view,
            "ctl00$ContentPlaceHolder1$ddlCiudades": _id,
        }
        r = session.post(page_url, data=data, cookies=cookies)
        tree = html.fromstring(r.text)

        divs = tree.xpath("//div[@class='col-md-4' and .//h3]")
        for d in divs:
            location_name = "".join(d.xpath(".//h3/text()")).strip()
            line = d.xpath(".//h3/following-sibling::span/text()")
            line = list(filter(None, [l.strip() for l in line]))

            street_address = line.pop(0)
            phone = line.pop(0).replace("Tel:", "").strip()
            hours_of_operation = line.pop(0).replace("Domicilios:", "").strip()

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                country_code="CO",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.papajohns.com.co/"
    page_url = "https://www.papajohns.com.co/FrmLocales.aspx"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
