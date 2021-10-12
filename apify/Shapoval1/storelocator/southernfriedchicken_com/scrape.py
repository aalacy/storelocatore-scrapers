import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://southernfriedchicken.com/"
    api_url = "https://southernfriedchicken.com/our-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath("//div/@data-mapdata"))
    js = json.loads(jsblock)
    for j in js["levels"][0]["locations"]:
        desc = j.get("description")
        a = html.fromstring(desc)

        page_url = (
            "".join(a.xpath('//a[contains(text(), "STORE PAGE")]/@href'))
            or "https://southernfriedchicken.com/our-locations/"
        )
        if page_url == "https://southernfriedchicken.com/?page_id=34906&preview=true":
            page_url = "https://southernfriedchicken.com/our-locations/"
        if (
            page_url
            == "https://southernfriedchicken.com/wp-content/uploads/2019/03/Alendvic-Menu.pdf"
        ):
            page_url = "https://southernfriedchicken.com/our-locations/"
        if page_url == "https://southernfriedchicken.com/?page_id=35894&preview=true":
            page_url = "https://southernfriedchicken.com/our-locations/"
        phone = (
            "".join(a.xpath('//p[contains(text(), "Tel")]/text()[1]'))
            .replace("Tel", "")
            .replace(":", "")
            .strip()
            or "<MISSING>"
        )

        hours_of_operation = (
            " ".join(
                a.xpath(
                    '//p[contains(text(), "Tel")]/following-sibling::p/text() | //p[contains(text(), "Monday")]/text()'
                )
            )
            .replace("\n", "")
            .replace("Social Medial Link:", "")
            .replace("Social media link:", "")
            .strip()
            or "<MISSING>"
        )

        location_name = "".join(j.get("title"))
        ad = (
            " ".join(a.xpath("//p[./a]/following-sibling::p[1]/text()"))
            .replace("\r\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(a.xpath("./p[1]/text()")).replace("\r\n", "").strip()
                or "<MISSING>"
            )
        if ad.find("Tel:") != -1:
            ad = "<MISSING>"
        if (
            ad == "<MISSING>"
            and page_url != "https://southernfriedchicken.com/our-locations/"
        ):
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            ad = (
                " ".join(
                    tree.xpath(
                        '//p[./span[contains(text(), "Tel")]]/preceding::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        try:
            country_code = location_name.split("(")[1].split(")")[0].strip()
        except:
            country_code = "<MISSING>"
        if "UAE" in location_name:
            country_code = "UAE"
        if "CHINA" in location_name:
            country_code = "CHINA"
        if "FRANCE" in location_name:
            country_code = "FRANCE"

        city = "<MISSING>"
        if ad != "<MISSING>":
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"

        if page_url == "https://southernfriedchicken.com/dobrynya-mall-perm-russia/":
            street_address = "Ursha Street, 62"
        if (
            page_url
            == "https://southernfriedchicken.com/trading-centre-mall-dushanbe-tajikistan/"
        ):
            street_address = "47 Dustii Khalkho str"
        if (
            page_url
            == "https://southernfriedchicken.com/kaliningrad-plaza-mall-kaliningrad-russia/"
        ):
            street_address = "Leninsky Prospect, 30"
        if page_url == "https://southernfriedchicken.com/lider-mall-kungur-russia/":
            street_address = "Bachurina Street, 56а"
        if page_url == "https://southernfriedchicken.com/real-mall-izhevsk-russia/":
            street_address = "Lenina Street, 136"
        if location_name == "RUDAKY, DUSHANBE (TAJIKISTAN)":
            street_address = "92 Rudaky Prospect"
        if (
            page_url
            == "https://southernfriedchicken.com/rudaky-prospect-dushanbe-tajikistan/"
        ):
            street_address = "30 Rudaky Prospect"
        if page_url == "https://southernfriedchicken.com/asia-park-almaty-kazakhstan/":
            street_address = "Rayimbek Ave 514"
        if (
            page_url
            == "https://southernfriedchicken.com/voroshilovsky-prospect-rostov-on-don-russia/"
        ):
            street_address = "105a Voroshilovsky Prospect"
        if page_url == "https://southernfriedchicken.com/melun-france/":
            street_address = "2 Place Saint Jean"
        if (
            page_url
            == "https://southernfriedchicken.com/gafurova-prospect-dushanbe-tajikistan/"
        ):
            street_address = "79/2 Nastatullo Mahsum Street"

        city = city.replace("Tyumenskaya", "").replace("Ghanjnsielem", "")
        if location_name.find("MARTINIQUE") != -1:
            city = "MARTINIQUE".capitalize()
            country_code = "FR"
        if location_name == "SHARJAH UAE":
            city = "SHARJAH".capitalize()
        if location_name == "WUSE 2, ABUJA (NIGERIA)":
            city = "ABUJA".capitalize()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        if phone == "<MISSING>":
            phone = (
                " ".join(
                    tree.xpath(
                        '//div[./p/span[contains(text(), "Tel")]]/p/span/text()[1]'
                    )
                )
                .replace("\n", "")
                .replace(":", "")
                .replace("Tel", "")
                .strip()
                or "<MISSING>"
            )
        if phone.count("+") > 1:
            phone = phone.split("+")[1].strip()
        if phone.find("  ") != -1:
            phone = phone.split("  ")[0].strip()
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//p[./span[contains(text(), "Opening Times")]]//text()')
                )
                .replace("\n", "")
                .replace("Opening Times:", "")
                .replace("Opening Times", "")
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
