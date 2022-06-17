from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://gusfriedchicken.com/"
    api_url = "https://gusfriedchicken.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="small-button smallsilver"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//title//text()"))
        if location_name.find("|") != -1:
            location_name = location_name.split("|")[0].strip()
        ad = (
            " ".join(tree.xpath('//*[contains(text(), "Store Address:")]//text()'))
            .replace("Store Address:", "")
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())

        location_type = "<MISSING>"
        temp_closed = tree.xpath(
            '//*[contains(text(), "Due to covid 19 we are closed until further notice")]'
        )
        if temp_closed:
            location_type = "temporarily closed"
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "")
            .replace("The Mall At Peachtree Center", "")
            .strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if street_address == "117 San":
            street_address = "117 San" + " " + str(city).split()[0].strip()
            city = str(city).split()[1].strip()
        geo = tree.xpath('//a[@title="Google Maps link"]/@href')
        if not geo:
            geo = tree.xpath('//a[contains(@href, "maps")]/@href')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo and "/@" in geo[0]:
            geo = geo[0].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        if longitude == "<MISSING>":
            geo = (
                tree.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            if "yelp.com" not in geo[0]:
                latitude = geo[1]
                longitude = geo[0]
        latitude = latitude.split("!")[0]
        phone = tree.xpath('//*[contains(text(), "Store Phone:")]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        hoo = tree.xpath('//div[p[contains(text(), "Store Hours:")]]/p/text()')
        if not hoo:
            hoo = tree.xpath('//div[contains(text(), "Store Hours:")]/p/text()')
            if "We fry" in hoo[0]:
                hoo = tree.xpath('//div[contains(text(), "Store Hours:")]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Store Hours: ")[-1].split(" We fry")[0]
            if hoo
            else "<MISSING>"
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
