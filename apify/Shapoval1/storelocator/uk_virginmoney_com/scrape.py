from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://uk.virginmoney.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://uk.virginmoney.com/store-finder/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    r = session.get(
        "https://uk.virginmoney.com/store-finder/search/all/", headers=headers
    )
    js = r.json()["BranchList"]

    for j in js:

        location_name = j.get("BranchName")
        store_number = j.get("BranchID")
        page_url = f"https://uk.virginmoney.com/virgin/store-finder/{store_number}.jsp"
        location_type = "Branch"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath('//h2[text()="Address"]/following-sibling::p[1]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if page_url == "https://uk.virginmoney.com/virgin/store-finder/280.jsp":
            city = "Baillieston"
        if (
            page_url == "https://uk.virginmoney.com/virgin/store-finder/281.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/238.jsp"
        ):
            street_address = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            state = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if (
            page_url == "https://uk.virginmoney.com/virgin/store-finder/340.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/26.jsp"
        ):
            city = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if (
            page_url.find("https://uk.virginmoney.com/virgin/store-finder/303.jsp")
            != -1
        ):
            street_address = street_address.replace("Milngavie", "").strip()
            city = "Milngavie"
        if page_url == "https://uk.virginmoney.com/virgin/store-finder/501.jsp":
            city = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if (
            page_url == "https://uk.virginmoney.com/virgin/store-finder/325.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/501.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/522.jsp"
        ):
            postal = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if (
            page_url == "https://uk.virginmoney.com/virgin/store-finder/520.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/303.jsp"
            or page_url == "https://uk.virginmoney.com/virgin/store-finder/341.jsp"
        ):
            postal = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if page_url == "https://uk.virginmoney.com/virgin/store-finder/522.jsp":
            street_address = (
                "".join(
                    tree.xpath(
                        '//h2[text()="Address"]/following-sibling::p[1]/text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + street_address
            )

        ll = "".join(tree.xpath('//div[@id="storefinder__map"]//img/@src'))
        try:
            latitude = ll.split("center=")[1].split(",")[0].strip()
            longitude = ll.split("center=")[1].split(",")[1].split("&")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath('//section[./h2[text()="Address"]]/table[1]//tr//text()')
            )
            .replace("\n", "")
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
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
