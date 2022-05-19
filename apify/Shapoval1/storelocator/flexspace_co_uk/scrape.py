from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://flexspace.co.uk/"
    api_url = "https://flexspace.co.uk/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var LocationData =")]/text()'))
        .split("var LocationData =")[1]
        .split(";")[0]
        .strip()
    )
    js = eval(div)

    for j in js:

        latitude = j[0]
        longitude = j[1]
        info = j[2]
        a = html.fromstring(info)
        page_url = "".join(a.xpath("//a/@href"))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        postal = (
            "".join(tree.xpath("//h1//a//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        location_name = (
            "".join(tree.xpath('//section[@class="bannerLocation"]/h2/text()'))
            .replace("\n", " ")
            .replace("\t", " ")
            .strip()
            or "<MISSING>"
        )
        location_name = " ".join(location_name.split())
        ad = (
            " ".join(
                "".join(tree.xpath("//h1//text()")).replace("\n", "").split(",")[1:]
            )
            .replace(f"{postal}", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "")
            .replace("L33 7Sy", "")
            .strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = " ".join(location_name.split()[1:]).strip()
        phone_lst = tree.xpath('//i[@class="fa fa-phone"]/following-sibling::a/text()')
        phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
        phone = "".join(phone_lst[0]).strip()

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
