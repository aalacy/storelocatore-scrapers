from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://bellacures.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[text()="Locations"]/following-sibling::div/ul/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
        except:
            continue

        location_name = "".join(
            tree.xpath('//div[@class="location-hero__content"]/h1/text()')
        )
        location_type = "Salon for hands and feet"
        ad = "".join(
            tree.xpath('//div[@class="location-hero__top-bar"]/div/a/text()')
        ).strip()
        street_address = ad
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "USA"
        city = "<MISSING>"
        if street_address.find(",") != -1:
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            state = ad.split(",")[2].split()[0].strip()
            postal = ad.split(",")[2].split()[1].strip()
        goo_link = "".join(
            tree.xpath('//div[@class="location-hero__top-bar"]/div/a/@href')
        ).strip()
        if state == "<MISSING>" and goo_link.find("google") != -1:
            state = goo_link.split("%2C+")[1].split("+")[0].strip()
            postal = goo_link.split("+")[-1].strip()
        if city == "<MISSING>":
            city = location_name
        if city.find("Dallas") != -1:
            city = "Dallas"

        try:
            if goo_link.find("ll=") != -1:
                latitude = goo_link.split("ll=")[1].split(",")[0]
                longitude = goo_link.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = goo_link.split("@")[1].split(",")[0]
                longitude = goo_link.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="location-hero__hours"]/span/text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("5th") != -1:
            hours_of_operation = hours_of_operation.split("5th")[1].strip()
        if hours_of_operation.find("APPOINTMENT") != -1:
            hours_of_operation = hours_of_operation.split("APPOINTMENT")[1].strip()
        hours_of_operation = hours_of_operation.replace("OPEN DAILY!", "").strip()

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://bellacures.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
