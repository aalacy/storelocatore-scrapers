from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.superhealthpharmacy.com/"
    api_url = "https://www.superhealthpharmacy.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Locations "]/following-sibling::ul/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.superhealthpharmacy.com{slug}"
        location_name = "".join(d.xpath(".//text()"))
        if "Coming" in location_name:
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Our")]/following-sibling::div/ul/li[1]//text()'
                )
            )
            .replace(",", "")
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Our")]/following-sibling::div/ul/li[2]//text()'
                )
            )
            + " "
            + "".join(
                tree.xpath(
                    '//h2[contains(text(), "Our")]/following-sibling::div/ul/li[3]//text()'
                )
            )
        )
        ad = ad.replace("Croton-On-Hudson", "Croton-On-Hudson,").strip()
        state = " ".join(ad.split(",")[1].split()[:-1])
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//h2[contains(text(), "Contact Us")]/following-sibling::div/ul/li[1]//text()'
                )
            )
            .replace("Phone:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "We\'re Open")]/following-sibling::div/ul/li//text()'
                )
            )
            .replace("\n", "")
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
            raw_address=f"{street_address} {city},{state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
