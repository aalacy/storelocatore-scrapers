from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.alcoa.com/"
    api_urls = [
        "https://www.alcoa.com/norway/no",
        "https://www.alcoa.com/spain/es",
        "https://www.alcoa.com/suriname/en",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    for api_url in api_urls:
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath("//p[./strong]")
        for d in div:

            page_url = api_url
            location_name = "".join(d.xpath("./strong[1]/text()"))
            ad = d.xpath("./strong[1]/following-sibling::text()")
            ad = list(filter(None, [a.strip() for a in ad]))
            try:
                adr = " ".join(ad).split("+")[0].replace("Teléfono:", "").strip()
            except:
                adr = " ".join(ad)
            a = parse_address(International_Parser(), adr)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = page_url.split("/")[-2].strip()
            city = a.city or "<MISSING>"
            if city.find("No-4552") != -1:
                city = city.replace("No-4552", "").strip()
                postal = "4552"
            if location_name.find("San Ciprián") != -1:
                street_address = "Calle Pedro Teixeira 8 Edificio Iberia Mart Planta 3"
                city = "Madrid"
                postal = "28020"
            phone = "<MISSING>"
            for a in ad:
                if "+" in a:
                    phone = str(a).replace("Teléfono:", "").strip()

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)

    locator_domain = "https://www.alcoa.com/"
    api_urls = [
        "https://www.alcoa.com/brasil/pt/contact",
        "https://www.alcoa.com/australia/en/contact",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    for api_url in api_urls:
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@style="font-weight: bold;"]')
        for d in div:

            page_url = api_url
            location_name = "".join(d.xpath(".//text()"))
            ad = d.xpath(".//following-sibling::div//text()")
            adr = []
            for a in ad:
                adr.append(a)
                if "+" in a or ") " in a:
                    break
            address = " ".join(adr[:-1])
            if location_name.find("(closed") != -1:
                continue
            if location_name.find("Corporate Office") != -1:
                continue
            if location_name.find("Alcoa of Australia") != -1:
                continue
            a = parse_address(International_Parser(), address)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                street_address = (
                    "".join(d.xpath(".//following-sibling::div[1]/text()"))
                    or "<MISSING>"
                )
            state = a.state or "<MISSING>"
            postal = a.postcode.replace("CEP", "").strip() or "<MISSING>"
            country_code = page_url.split("/")[-3].strip()
            city = a.city or "<MISSING>"
            phone = "".join(adr[-1]).replace("Phone:", "").strip()
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            hours_of_operation = "<MISSING>"
            if street_address.find("Closed Under Decommission") != -1:
                street_address = street_address.replace(
                    "Closed Under Decommission", ""
                ).strip()
                hours_of_operation = "Closed"

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

    locator_domain = "https://www.alcoa.com/"
    api_url = "https://www.alcoa.com/saudi-arabia/en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[contains(text(), "Location")]/following::div[./p][1]/p[1]')
    for d in div:

        page_url = api_url
        location_name = "<MISSING>"
        address = " ".join(d.xpath(".//text()[2]")).replace("\n", "").strip()
        a = parse_address(International_Parser(), address)
        street_address = "".join(d.xpath(".//text()[1]")).replace("\n", "").strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = page_url.split("/")[-2].strip()
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath(".//text()[last()]"))
            .replace("\n", "")
            .replace("++", "+")
            .strip()
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
