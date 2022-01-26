from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.curvesafrica.com"
    api_url = "https://www.curvesafrica.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@name="country"]/option[position() > 1]')
    for d in div:
        country_code = "".join(d.xpath(".//@value"))
        country_url = f"https://www.curvesafrica.com/locations?country={country_code}"
        r = session.get(country_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//select[@name="province"]/option[position() > 1] | //option[text()="Please select a club"]'
        )
        for d in div:

            state_val = "".join(d.xpath(".//@value")).replace("0", "") or "<MISSING>"
            state = (
                "".join(d.xpath(".//text()"))
                .replace("Please select a club", "")
                .strip()
                or "<MISSING>"
            )
            state_url = country_url
            if state_val != "<MISSING>":
                state_url = f"https://www.curvesafrica.com/locations?country={country_code}&province={state_val}"
            r = session.get(state_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//select[@name="club"]/option[position() > 1]')
            for d in div:
                city = "".join(d.xpath(".//text()")) or "<MISSING>"
                slug = "".join(d.xpath(".//@value")) or "<MISSING>"
                page_url = f"https://www.curvesafrica.com/locations?country={country_code}&province={state_val}&club={slug}"
                if state_val == "<MISSING>":
                    page_url = f"https://www.curvesafrica.com/locations?country={country_code}&club={slug}"
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                ad = (
                    " ".join(
                        tree.xpath(
                            '//div[@class="franchise-info"]/div[not(@class)]/text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                ad = " ".join(ad.split())
                if ad.endswith(",") != -1:
                    ad = "".join(ad[:-1])

                location_name = (
                    "".join(tree.xpath('//div[@class="name"]/text()')).strip()
                    or "<MISSING>"
                )
                if location_name.endswith(",") != -1:
                    location_name = "".join(location_name[:-1])
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                postal = a.postcode or "<MISSING>"
                text = "".join(
                    tree.xpath(
                        '//script[contains(text(), "initializeGoogleMap(")]/text()'
                    )
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                if text:
                    latitude = text.split("(")[1].split(",")[0].strip()
                    longitude = text.split("(")[1].split(",")[1].strip()
                if latitude == "1" or longitude == "1":
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = (
                    "".join(tree.xpath('//div[@class="tel"]/text()'))
                    .replace("Tel:", "")
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
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
