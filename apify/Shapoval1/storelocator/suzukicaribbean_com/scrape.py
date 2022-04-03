from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.suzukicaribbean.com/"
    api_url = "https://www.suzukicaribbean.com/en/home?country=bs"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="select_country"]/option')
    for d in div:
        country_code = "".join(d.xpath(".//text()"))
        slug = "".join(d.xpath(".//@data-url"))
        page_url = f"https://www.suzukicaribbean.com/{slug}".replace(
            "home", "contact"
        ).replace("accueil", "contact")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath(
                '//h3[text()="ADDRESS"]/following-sibling::h2[1]/text() | //h3[text()="ADRESSE"]/following-sibling::h2[1]/text()'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h3[text()="ADDRESS"]/following-sibling::h3[1]/text() | //h3[text()="ADRESSE"]/following-sibling::h3[1]/text()'
                )
            )
            .replace("\n", "")
            .replace("&NBSP;", "")
            .replace("&AMP;", "&")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if page_url == "https://www.suzukicaribbean.com/en/contact?country=ai":
            street_address = " ".join(ad.split(",")[1].split()[:-1]).strip()
            city = ad.split(",")[0].strip()
        if page_url == "https://www.suzukicaribbean.com/fr/contact?country=mq":
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].split()[1].strip()
            postal = ad.split(",")[1].split()[0].strip()
        if page_url == "https://www.suzukicaribbean.com/en/contact?country=kn":
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
        if page_url == "https://www.suzukicaribbean.com/en/contact?country=vc":
            street_address = ad.split(",")[1].split(".")[0].strip()
            city = ad.split(",")[1].split(".")[1].strip()
        if "SAN JUAN" in ad:
            city = "San Juan"
        if postal == "4":
            postal = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "".join(
            tree.xpath(
                '//div[@class="title-box text-left text-mdd-center"]//h3[contains(text(), "PHONE")]/text()'
            )
        )
        if phone.find("PHONE") != -1:
            phone = phone.split("PHONE")[1].strip()
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//h3[text()="ADDRESS"]/following-sibling::h3[2]/text() | //h3[text()="ADRESSE"]/following-sibling::h3[2]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
