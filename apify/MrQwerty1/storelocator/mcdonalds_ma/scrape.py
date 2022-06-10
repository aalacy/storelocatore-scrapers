from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://www.mcdonalds.ma/nos-restaurants/r%C3%A9seau-maroc"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='cont_restau_infos']")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='restauName']/text()")).strip()
        phone = SgRecord.MISSING

        line = d.xpath(".//div[@class='info_resto']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            street_address, city, state, postal = (
                SgRecord.MISSING,
                SgRecord.MISSING,
                SgRecord.MISSING,
                SgRecord.MISSING,
            )
        else:
            if "Fax" in line[-1]:
                line.pop()
            if "Tél" in line[-1]:
                phone = line.pop().split(":")[-1].strip()
            ad = ", ".join(line)
            street_address, city, state, postal = get_international(ad)

        text = "".join(d.xpath(".//div[@class='linktomap']/a/@href"))
        try:
            latitude = text.split("al=")[1].split("&")[0].strip()
            longitude = text.split("lo=")[1].split("&")[0].strip()
        except IndexError:
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING

        try:
            source = "<b>".join(html.tostring(d).decode("utf8").split("<b>")[1:]).split(
                "-->"
            )[0]
            root = html.fromstring(source)
            text = "".join(root.xpath("//text()"))
            text = " ".join(text.split()).lower()
            if "dimanche" not in text:
                hours_of_operation = text.split("7j/7 :")[1].strip()
                if "_" in text:
                    hours_of_operation = hours_of_operation.split("_")[0].strip()
                else:
                    hours_of_operation = hours_of_operation.split("m")[0].strip()
            else:
                hours_of_operation = " ".join(
                    ";".join(text.split("ventes à emporter")[1:]).split()
                )
        except:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="MA",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.mcdonalds.ma/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
