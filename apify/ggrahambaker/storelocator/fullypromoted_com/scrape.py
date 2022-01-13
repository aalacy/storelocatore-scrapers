from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fullypromoted.com"
    api_urls = [
        "https://fullypromoted.com/locations/",
        "https://fullypromoted.com/locations/country/mex/",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[./div[@class="col-md-6"]]')
        for d in div:
            slug = "".join(d.xpath('./div[@class="col-md-6"]/a/@href'))
            page_url = "https://fullypromoted.com/locations/country/mex/"
            if slug.find("locations") != -1:
                page_url = f"https://fullypromoted.com{slug}"

            location_name = (
                "Fully Promoted "
                + "".join(d.xpath('.//div[@class="col-md-6"]//text()'))
                .replace("\n", "")
                .strip()
            )
            adr = (
                " ".join(d.xpath('.//div[@class="col-md-6 text-right"]/text()'))
                .replace("\n", "")
                .strip()
            )
            adr = " ".join(adr.split())
            a = parse_address(International_Parser(), adr)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            if state == "IL":
                country_code = "US"
            if page_url.find("mex") != -1:
                country_code = "Mexico"
            city = a.city or "<MISSING>"
            if city == "<MISSING>" and page_url.find("mex") != -1:
                city = adr.split(",")[0].split()[-1].strip()
                state = adr.split(",")[1].split()[0].strip()
                postal = adr.split(",")[1].split()[1].strip()
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            if page_url.find("mex") == -1:
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                try:
                    latitude = (
                        "".join(
                            tree.xpath(
                                '//script[contains(text(), "ProfessionalService")]/text()'
                            )
                        )
                        .split('"latitude":')[1]
                        .split(",")[0]
                        .strip()
                    )
                    longitude = (
                        "".join(
                            tree.xpath(
                                '//script[contains(text(), "ProfessionalService")]/text()'
                            )
                        )
                        .split('"longitude":')[1]
                        .split("}")[0]
                        .strip()
                    )
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                hours_of_operation = (
                    " ".join(tree.xpath("//table//tr/td/text()"))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = " ".join(hours_of_operation.split())
                if street_address == "<MISSING>":
                    street_address = (
                        "".join(
                            tree.xpath(
                                '//div[@class="pt-2 pb-4 px-4"]/h4[1]/following::p[1]/span/text()'
                            )
                        )
                        or "<MISSING>"
                    )
                    ad = (
                        "".join(
                            tree.xpath(
                                '//div[@class="pt-2 pb-4 px-4"]/h4[1]/following::p[1]/text()'
                            )
                        )
                        .replace("\n", "")
                        .replace("\r", "")
                        .strip()
                    )
                    state = ad.split(",")[1].split()[0].strip()
                    postal = " ".join(ad.split(",")[1].split()[1:]).strip()
                    country_code = "CA"
                    if state == "IL":
                        country_code = "US"
                    city = ad.split(",")[0].strip()

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
