from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.americangirl.com/"
    page_url = "https://www.americangirl.com/pages/retail-canada"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h6/a]")
    for d in div:

        location_name = "".join(d.xpath(".//h6//text()")).replace("\n", "").strip()
        ad = d.xpath(".//h6/following-sibling::p[1]//text()")
        ad = list(filter(None, [a.strip() for a in ad]))

        phone = "".join(ad[-1]).strip()
        adr = "".join(ad[1]).strip()
        street_address = "".join(ad[0]).strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = " ".join(adr.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = adr.split(",")[0].strip()
        text = "".join(d.xpath(".//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

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

    locator_domain = "https://www.americangirl.com/"
    api_url = "https://www.americangirl.com/pages/retail"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//main/section[1]//section[1]/h3[contains(text(), "Choose a location")]/following-sibling::ul/li//a'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.americangirl.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(tree.xpath('//main[@id="main"]//div[./h2]//h2//text()'))
            .replace("\n", "")
            .replace("Hotels full of hospitality", "")
            .strip()
            or "<MISSING>"
        )
        ad = tree.xpath(
            '//main[@id="main"]//div[./h2]//h2/following-sibling::div[1]/p//text()'
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        if not ad:
            continue
        phone = "".join(ad[-1]).strip()
        adr = " ".join(ad).split(f"{phone}")[0].strip()

        street_address = adr.split(",")[0].replace("136 th", "136th").strip()
        state = adr.split(",")[-1].split()[0].strip()
        postal = adr.split(",")[-1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[1].strip()
        with SgFirefox() as driver:

            driver.get(page_url)
            a = driver.page_source
            tree = html.fromstring(a)

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//span[contains(text(), "Store Hours")]/following-sibling::span//text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
