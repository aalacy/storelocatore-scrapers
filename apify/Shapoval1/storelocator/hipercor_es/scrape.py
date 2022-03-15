import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.elcorteingles.es"
    api_url = "https://www.elcorteingles.es/centroscomerciales/es/hipercor"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="home-centers-list"]/div/div/ul/li')
    for d in div:
        state = "".join(d.xpath(".//span/text()"))
        cities = d.xpath(".//following-sibling::ul/li/a")
        for c in cities:
            slug = "".join(c.xpath(".//@href"))
            page_url = f"https://www.elcorteingles.es{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//h1/text()"))
            loc = tree.xpath(
                '//*[./i[@class="fa fa-map-marker"]]/following-sibling::*[1]'
            )
            for l in loc:

                ad = "".join(l.xpath(".//text()"))
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                postal = a.postcode or "<MISSING>"
                country_code = "ES"
                city = a.city or "<MISSING>"
                if street_address.find("29651 Las") != -1:
                    postal = ad.split(",")[2].split()[0].strip()
                    street_address = " ".join(ad.split(",")[:2]).strip()
                ll = "".join(l.xpath(".//following::div/@data-location"))
                j = json.loads(ll)
                latitude = j.get("lat") or "<MISSING>"
                longitude = j.get("lng") or "<MISSING>"
                phone = (
                    "".join(l.xpath(".//following::a[1]/text()"))
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(
                    l.xpath(
                        './/following::h2[text()="Calendario de apertura"][1]/following-sibling::ul[1]/li/*/text()'
                    )
                ).strip()
                hours_of_operation = (
                    " ".join(hours_of_operation.split())
                    .replace("Consultar domingos y festivos de apertura", "")
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
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
