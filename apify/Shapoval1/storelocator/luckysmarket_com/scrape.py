from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.luckysmarket.com/"
    api_url = "https://www.luckysmarket.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./div/div/p[contains(text(), "STORES")]]/following-sibling::ul/li/a'
    )

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("https://www.luckysmarket.com/store-tour") != -1:
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//span[@style="font-size:52px"]//text()'))
        street_address = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "ADDRESS")]]/following-sibling::p[1]//text()'
            )
        )
        ad = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "ADDRESS")]]/following-sibling::p[2]//text()'
            )
        )

        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = ad.split(",")[1].split()[1].strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[.//span[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.replace(
            "Take Out & Indoor Dining", ""
        ).strip()
        phone = "".join(
            tree.xpath(
                '//p[.//span[contains(text(), "PHONE")]]/following-sibling::p[1]//text()'
            )
        )
        store_number = "<MISSING>"
        api_url2 = "https://api.freshop.com/1/stores?app_key=luckys_market&has_address=true&limit=10&token=355d3f4fb7329e1bc1767cefec756e85"
        session = SgRequests()
        r = session.get(api_url2, headers=headers)
        js = r.json()["items"]
        for j in js:
            adr = j.get("address_1")
            if adr == street_address:
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                store_number = j.get("store_number")

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.luckysmarket.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
