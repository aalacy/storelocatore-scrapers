from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_coords(_id):
    r = session.get(
        f"https://www.papajohns.com.ec/index.php?com=contenido&fun=sucursal_mapa&id={_id}",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script/text()"))

    return eval(text.split("L.marker(")[1].split(")")[0])


def fetch_data(sgw: SgWriter):
    page_url = "https://www.papajohns.com.ec/index.php?com=contenido&fun=sucursales#"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='section SucDir']")

    for d in divs:
        location_name = "".join(d.xpath("./div[1]/h3/text()")).strip()
        street_address = "".join(d.xpath("./div[1]/div/div[2]/text()")).strip()
        phone = "".join(d.xpath("./div[1]/div/div[last()]/text()")).strip()
        store_number = "".join(d.xpath("./@id")).split("-")[-1]
        latitude, longitude = get_coords(store_number)
        city = "".join(
            tree.xpath(
                f"//div[contains(@class, 'panel ') and .//a[@data-idsucursal='{store_number}']]//h3/a/text()"
            )
        ).strip()

        inters = d.xpath("./div[2]/div/div/text()")
        inters = list(filter(None, [inter.strip() for inter in inters]))
        hours_of_operation = " - ".join(inters)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="EC",
            store_number=store_number,
            phone=phone,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    locator_domain = "https://www.papajohns.com.ec/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
