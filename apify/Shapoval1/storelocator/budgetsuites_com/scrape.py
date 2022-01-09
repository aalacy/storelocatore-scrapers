from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://budgetsuites.com/locations.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="form-group"]')

    for d in div:
        slug = "".join(d.xpath(".//label/@for"))
        session = SgRequests()
        r = session.get(
            f"http://www.budgetsuites.com/state_locations.php?name={slug}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        divs = tree.xpath('//span[@class="name"]/a')
        for k in divs:
            page_url = "https://budgetsuites.com/" + "".join(k.xpath("./@href"))
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//h1/text()")).split("the")[1].strip()
            street_address = "".join(tree.xpath('//p[@class="info"]/a[1]/text()[1]'))
            ad = (
                "".join(tree.xpath('//p[@class="info"]/a[1]/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            phone = (
                "".join(
                    tree.xpath('//p[@class="info"]/a[contains(@href, "tel")]/text()[1]')
                )
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            hours_of_operation = (
                "".join(tree.xpath('//div[contains(text(), "Office hours:")]/text()'))
                .replace("Office hours:", "")
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
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://budgetsuites.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
