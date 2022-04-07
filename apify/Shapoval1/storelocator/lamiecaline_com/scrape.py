from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lamiecaline.com/"
    api_url = "https://www.lamiecaline.com/wp-admin/admin-ajax.php?action=get_franchise_markers"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        store_number = j.get("ID") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        sub_page_url = f"https://www.lamiecaline.com/wp-admin/admin-ajax.php?action=get_unique_franchise_listing&franchise={store_number}"
        r = session.get(sub_page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = tree.xpath("//h2//text()")
        info_url = tree.xpath("//h2//a//@href")
        info = list(filter(None, [a.strip() for a in info]))
        ad = "".join(info[-1]).strip()
        page_url = "".join(info_url[0]).strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FR"
        city = a.city or "<MISSING>"
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad.split(f"{postal}")[0].strip()
        if page_url == "https://www.lamiecaline.com/boutiques/lile-dyeu/":
            postal = "85350"
            street_address = ad.split(f"{postal}")[0].strip()
            city = ad.split(f"{postal}")[1].split(",")[0].strip()
        if page_url == "https://www.lamiecaline.com/boutiques/agen-centre-ville/":
            postal = "4700"
            street_address = ad.split(f"{postal}")[0].strip()
            city = ad.split(f"{postal}")[1].split(",")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//li[./a/span[@class="elementor-icon-list-icon"]]/a[contains(@href, "tel")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath('//div[@class="jet-toggle__content-inner"]//div//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=SgRecord.MISSING,
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
