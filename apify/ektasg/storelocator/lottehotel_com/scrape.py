from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lottehotel.com"
    api_url = "https://www.lottehotel.com/global/en/hotel-finder.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@class, "hotel__image")]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = slug
        if page_url.find("http") == -1:
            page_url = f"https://www.lottehotel.com{slug}"
        country_code = "".join(
            d.xpath('.//preceding::strong[contains(@class, "nation__title")][1]/text()')
        )
        if country_code == "Global":
            country_code = (
                "".join(
                    d.xpath(
                        './/preceding::button[contains(@class, "-city__title")][1]/text()'
                    )
                )
                .split("(")[0]
                .strip()
            )

        location_name = "".join(
            d.xpath(
                './/following::p[contains(@class, "hotel__title")][1]//strong/text()'
            )
        )
        phone = (
            "".join(
                d.xpath('.//following::p[contains(@class, "hotel__tel")][1]/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            "".join(
                d.xpath(
                    './/following::p[contains(@class, "hotel__address")][1]//text()'
                )
            )
            or "<MISSING>"
        )
        if ad == "<MISSING>" and location_name == "LOTTE RESORT BUYEO":
            session = SgRequests()
            r = session.get("https://www.lotteresort.com/buyeo/en/about")
            tree = html.fromstring(r.text)
            ad = (
                "".join(tree.xpath('//strong[contains(text(), "Address")]/text()'))
                .replace("Address :", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if location_name == "LOTTE RESORT JEJU ART VILLAS":
            street_address = " ".join(ad.split(",")[1:3]).strip()
        if location_name == "LOTTE City Hotel Mapo":
            street_address = " ".join(ad.split(",")[0:2]).strip()
        if location_name == "LOTTE City Hotel Kinshicho":
            street_address = ad.split(",")[0].strip()

        state = a.state or "<MISSING>"
        if location_name == "LOTTE HOTEL GUAM":
            state = ad.split(",")[1].split()[0].strip()
        postal = a.postcode or "<MISSING>"
        city = a.city
        if country_code == "Korea":
            city = (
                "".join(
                    d.xpath(
                        './/preceding::button[contains(@class, "-city__title")][1]/text()'
                    )
                )
                .split("(")[0]
                .strip()
            )
        if (
            page_url == "https://www.lotteresort.com/main/en/index"
            and location_name == "LOTTE RESORT JEJU ART VILLAS"
        ):
            page_url = "https://www.lotteresort.com/artvillas/en/about"
        if (
            page_url == "https://www.lotteresort.com/main/en/index"
            and location_name == "LOTTE RESORT SOKCHO"
        ):
            page_url = "https://www.lotteresort.com/sokcho/en/about"
        if (
            page_url == "https://www.lotteresort.com/main/en/index"
            and location_name == "LOTTE RESORT BUYEO"
        ):
            page_url = "https://www.lotteresort.com/buyeo/en/about"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(tree.xpath('//input[@id="locationLat"]/@value')) or "<MISSING>"
        )
        longitude = (
            "".join(tree.xpath('//input[@id="locationLng"]/@value')) or "<MISSING>"
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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
