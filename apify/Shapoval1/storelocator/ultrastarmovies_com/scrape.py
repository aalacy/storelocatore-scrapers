from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ultrastarmovies.com/#"
    api_url = "https://ultrastarus.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[./span[text()="Visit Site"]]')
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://ultrastarus.com{slug}"
        if page_url.count("https") > 1:
            continue
        location_name = "".join(d.xpath(".//preceding::h1[1]//text()")).strip()
        if page_url.find("valleyriver") != -1:
            page_url = page_url.replace("valleyriver", "valley-river")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        street_address = "".join(
            tree.xpath(
                '////div[@class="fusion-column-wrapper fusion-flex-justify-content-center fusion-content-layout-column"]//h4[1]/span[1]/text()'
            )
        )
        ad = "".join(
            tree.xpath(
                '////div[@class="fusion-column-wrapper fusion-flex-justify-content-center fusion-content-layout-column"]//h4[1]/span[2]/text()'
            )
        )
        phone = "".join(
            tree.xpath(
                '//div[contains(@class, "fusion-text fusion-text-")]//h4[2]//text()'
            )
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].split()[-1].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "fusion-text fusion-text-")]//span[./strong[text()="CURRENT HOURS"]]/following-sibling::span//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
