import urllib.parse
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://subway.ru"
    api_url = "https://subway.ru/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="shops"]/li/a')
    for d in div:
        slug1 = "".join(d.xpath(".//@href")).split("=")[1].strip()
        slug = urllib.parse.urlencode({"q": f"{slug1}"})

        city = "".join(d.xpath(".//text()"))
        spage_url = f"https://subway.ru/stores/?{slug}".replace("q=q=", "q=").strip()
        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="catalog-list__item restaurant-card"]/a')
        for d in div:

            slug = "".join(d.xpath(".//@href"))
            page_url = f"https://subway.ru{slug}"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = (
                "".join(tree.xpath('//div[@class="restaurant-detail__title"]/text()'))
                .replace("\n", "")
                .strip()
            )
            ad = (
                " ".join(
                    tree.xpath(
                        '//ul[@class="restaurant-detail__contacts-list"]/li[1]//div[@class="restaurant-detail__contacts-list-item-value"]/text()'
                    )
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
            if ad[0].isdigit():
                postal = ad.split(",")[0].strip()
            country_code = "RU"

            try:
                latitude = (
                    "".join(tree.xpath('//script[contains(text(), "center:")]/text()'))
                    .split("center: [")[1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(tree.xpath('//script[contains(text(), "center:")]/text()'))
                    .split("center: [")[1]
                    .split(",")[1]
                    .split("]")[0]
                    .strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//ul[@class="shop__details__timetable__list"]/li//span/text()'
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
