from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mclaneco.com"
    page_url = "https://www.mclaneco.com/content/mclaneco/en/locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var locationsFS")]/text()'))
        .split("var locationsFS = ")[1]
        .split("];")[0]
        .replace("&#58;", ":")
        .replace(' style="color: #ee352a;"', "")
        .replace(", , ", "")
        + "]"
    )
    div_l = eval(div)

    for d in div_l:

        tree = html.fromstring(str(d))
        location_name = "".join(tree.xpath("//b//text()"))
        if not location_name:
            continue
        location_type = "McLane Foodservice"
        street_address = (
            "".join(tree.xpath("//b/following-sibling::text()[1]"))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath("//b/following-sibling::text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        try:
            latitude = str(d).split(",")[-2].split(",")[0].strip()
            longitude = str(d).split(",")[-1].replace("]", "").strip()
        except IndexError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if not latitude.replace(".", "").isdigit():
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone_ls = tree.xpath('//a[contains(@href, "tel")]/text()')
        try:
            phone = "".join(phone_ls[0]).strip()
        except IndexError:
            phone = "<MISSING>"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)

    locator_domain = "https://www.mclaneco.com"
    page_url = "https://www.mclaneco.com/content/mclaneco/en/locations.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var locationsFS")]/text()'))
        .split("var locationsGR = ")[1]
        .split("];")[0]
        .replace("&#58;", ":")
        .replace(' style="color: #ee352a;"', "")
        .replace(", , ", "")
        + "]"
    )
    div_l = eval(div)

    for d in div_l:

        tree = html.fromstring(str(d))
        location_name = "".join(tree.xpath("//b//text()"))
        if not location_name:
            continue
        location_type = "McLane Grocery"
        street_address = (
            "".join(tree.xpath("//b/following-sibling::text()[1]"))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath("//b/following-sibling::text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if ad == "Business Park":
            ad = (
                "".join(tree.xpath("//b/following-sibling::text()[3]"))
                .replace("\n", "")
                .strip()
            )
        try:
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
        except:
            print(ad, street_address)
        try:
            latitude = str(d).split(",")[-2].split(",")[0].strip()
            longitude = str(d).split(",")[-1].replace("]", "").strip()
        except IndexError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if not latitude.replace(".", "").isdigit():
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone_ls = tree.xpath('//a[contains(@href, "tel")]/text()')
        try:
            phone = "".join(phone_ls[0]).strip()
        except IndexError:
            phone = "<MISSING>"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
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
