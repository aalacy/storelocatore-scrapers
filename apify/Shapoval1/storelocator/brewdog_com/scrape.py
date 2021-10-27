from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_urls = [
        "https://www.brewdog.com/uk/bar_pages/bar/locator/view_all/1/",
        "https://www.brewdog.com/uk/bar_pages/bar/locator/filter/usa/view_all/1/",
        "https://www.brewdog.com/uk/bar_pages/bar/locator/filter/global/view_all/1/",
        "https://www.brewdog.com/uk/bar_pages/bar/locator/filter/coming-soon/view_all/1/",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    for api_url in api_urls:
        session = SgRequests()
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        block = tree.xpath("//div[@class='bar-listing__results__bar']")
        for b in block:

            address = "".join(
                b.xpath(
                    './/div[@class="bar-listing__results__bar__detail md:justify-start md:text-left"]/p/text()'
                )
            )
            a = parse_address(International_Parser(), address)
            country_code = a.country or "<MISSING>"
            location_name = (
                "".join(
                    b.xpath('.//h5[@class="heading heading-5 md:text-left"]/text()')
                )
                or "<MISSING>"
            )
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            city = a.city or "<MISSING>"
            if city == "Manchester Manchester":
                city = "Manchester"
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            phone = (
                "".join(
                    b.xpath(
                        ".//div[@class='bar-listing__results__bar__detail md:justify-start']/p/text()"
                    )
                )
                or "<MISSING>"
            )
            cms = "".join(
                b.xpath(
                    './/img[@src="//images.ctfassets.net/b0qgo9rl751g/7DSPQnbuuQAA0enZ9b3uIH/041c62f2e724e3a08f5f9263246349d5/Bar_shields_for_website.png"]/@src'
                )
            )

            page_url = "".join(
                b.xpath(
                    './/div[@class="bar-listing__results__bar__buttons md:text-left"]/a[@class="button button--tertiary bar-listing__results__bar__buttons__view"]/@href'
                )
            )
            if page_url == "https://www.brewdog.com/uk/bars/usa/new-albany/":
                page_url = (
                    "https://www.brewdog.com/uk/bar_pages/bar/locator/view_all/1/"
                )
            if page_url == "https://www.brewdog.com/uk/bars/uk/dogtap-ellon-brewdog/":
                page_url = (
                    "https://www.brewdog.com/uk/bar_pages/bar/locator/view_all/1/"
                )
            if page_url.find("coming-soon") != -1:
                page_url = "https://www.brewdog.com/uk/bar_pages/bar/locator/filter/coming-soon/view_all/1/"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tres = html.fromstring(r.text)
            text = "".join(tres.xpath('//iframe[@class="bar-detail__map"]/@src'))
            try:
                if text.find("q=") != -1:
                    latitude = text.split("q=")[1].split(",")[0]
                    longitude = text.split("q=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"

            hours_of_operation = (
                " ".join(tres.xpath('//p[@class="copy text-white"]/text()'))
                .replace("\n", " ")
                .strip()
            )
            hours_of_operation = (
                hours_of_operation.replace("AM", " AM ")
                .replace("PM", " PM ")
                .replace(" ", "")
                or "<MISSING>"
            )
            hours_of_operation = (
                hours_of_operation.replace("Monday:", "Monday: ")
                .replace("Tuesday:", " Tuesday: ")
                .replace("Wednesday:", " Wednesday: ")
                .replace("Thursday:", " Thursday: ")
                .replace("Friday:", " Friday: ")
                .replace("Saturday:", " Saturday: ")
                .replace("Sunday:", " Sunday: ")
            )
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

            tcls = "".join(
                tres.xpath(
                    '//p[text()=" Currently closed "]/text() | //p[text()="We have no kitchen at this time "]/text()'
                )
            )
            if tcls:
                hours_of_operation = "Currently closed"
            if cms:
                hours_of_operation = "Coming Soon"
            if page_url.find("coming-soon") != -1:
                hours_of_operation = "Coming Soon"
            if page_url.find("/uk/bars/uk/") and country_code == "<MISSING>":
                country_code = "GB"

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
    locator_domain = "https://www.brewdog.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
