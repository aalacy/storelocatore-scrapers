from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_url = "https://tapsfishhouse.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[text()="Locations"]/following::ul[1]/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(tree.xpath('//h2[@class="av-special-heading-tag "]/text()'))
            .replace("\n", "")
            .strip()
        )

        country_code = "US"
        ad = "".join(tree.xpath("//div[./h2]/following-sibling::div[1]//a/text()"))
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        text = "".join(tree.xpath("//div[./h2]/following-sibling::div[1]//a/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(tree.xpath("//div[./h2]/following-sibling::div[2]//a/text()"))
        hours_of_operation = tree.xpath(
            '//div[@id="av_section_5"]//div[./div[contains(@class, "flex_column av_one_fifth")]]/div//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation[0:6])
            + " "
            + " ".join(hours_of_operation[13:18])
        )
        if location_name.find("Opening Soon") != -1:
            hours_of_operation = "Coming Soon"
            location_name = (
                location_name.replace("– Opening Soon", "")
                .replace("Opening Soon", "")
                .strip()
            )
        if (
            page_url == "https://tapsfishhouse.com/taps-fish-house-brewery-scottsdale/"
            and hours_of_operation == "Coming Soon"
        ):
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://tapsfishhouse.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
