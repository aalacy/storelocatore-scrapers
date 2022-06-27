from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tesla.com/"
    api_url = "https://www.tesla.com/findus/list"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h2[contains(text(), "Tesla Superchargers")]/following-sibling::div[1]//a'
    )
    for d in div:
        sub_page_url_slug = "".join(d.xpath(".//@href"))
        sub_page_url = f"https://www.tesla.com{sub_page_url_slug}"
        country_code = sub_page_url.split("/")[-1].replace("+", " ").strip()
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//address[@class="vcard"]')
        for d in div:

            slug = "".join(d.xpath("./a[1]/@href"))
            page_url = f"https://www.tesla.com{slug}"
            location_name = "".join(d.xpath("./a[1]/text()"))
            if "coming soon" in location_name:
                continue
            ad = (
                " ".join(d.xpath('.//span[@class="adr"]//text()'))
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split())

            a = parse_address(International_Parser(), ad)
            street_address = (
                " ".join(d.xpath('.//span[@class="street-address"]//text()'))
                .replace("\n", "")
                .strip()
            )
            street_address = " ".join(street_address.split()) or "<MISSING>"
            if street_address == "<MISSING>":
                continue
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"
            phone_l = d.xpath('.//span[@class="value"]//text()')
            phone_l = list(filter(None, [b.strip() for b in phone_l]))
            phone = "<MISSING>"
            if phone_l:
                phone = "".join(phone_l[0]).strip()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            ll = "".join(tree.xpath('//img[contains(@src, "maps")]/@src'))
            try:
                latitude = ll.split("center=")[1].split(",")[0].strip()
                longitude = ll.split("center=")[1].split(",")[1].split("&")[0].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            try:
                store_number = page_url.split("/")[-1].strip()
            except:
                store_number = "<MISSING>"
            location_type = "Supercharger"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
