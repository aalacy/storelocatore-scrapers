from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://earlofsandwichusa.com/"
    api_url = "https://locations.earlofsandwichusa.com/index.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="c-directory-list-content"]/li//a')
    for d in div:
        country_url = "".join(d.xpath(".//@href"))
        if country_url.find("/") != -1:
            country_url = country_url.split("/")[0].strip()
        country_url = "https://locations.earlofsandwichusa.com/" + country_url
        country_code = "".join(d.xpath(".//text()"))
        r = session.get(country_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//ul[@class="c-directory-list-content"]/li//a')
        for d in div:
            state_slug = "".join(d.xpath(".//@href"))
            if state_slug.count("/") > 1:
                state_slug = "/".join(state_slug.split("/")[:2])
            state_url = "https://locations.earlofsandwichusa.com/" + state_slug
            r = session.get(state_url, headers=headers)
            tree = html.fromstring(r.text)
            div = tree.xpath('//ul[@class="c-directory-list-content"]/li//a')
            for d in div:
                city_slug = "".join(d.xpath(".//@href")).replace("../", "").strip()
                if city_slug.count("/") > 1:
                    city_slug = "/".join(city_slug.split("/")[:3])
                city_url = "https://locations.earlofsandwichusa.com/" + city_slug
                r = session.get(city_url, headers=headers)
                tree = html.fromstring(r.text)
                div = tree.xpath('//article[@class="Teaser"]')
                for d in div:
                    page_slug = "".join(
                        d.xpath('.//div[@class="Teaser-link Teaser-page"]/a/@href')
                    ).replace("../../", "")
                    page_url = city_url
                    if page_slug:
                        page_url = page_slug
                        if page_url.find("http") == -1:
                            page_url = (
                                "https://locations.earlofsandwichusa.com/" + page_slug
                            )

                    location_name = (
                        " ".join(d.xpath('.//span[@class="LocationName"]//text()'))
                        .replace("\n", "")
                        .strip()
                    )
                    location_name = " ".join(location_name.split())
                    street_address = (
                        " ".join(d.xpath('.//span[@class="c-address-street"]//text()'))
                        .replace("\n", "")
                        .strip()
                    )
                    street_address = " ".join(street_address.split())
                    state = (
                        "".join(d.xpath('.//abbr[@class="c-address-state "]//text()'))
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )
                    postal = (
                        "".join(
                            d.xpath('.//span[@class="c-address-postal-code "]//text()')
                        )
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )
                    city = (
                        "".join(
                            d.xpath(
                                './/span[contains(@class, "c-address-city")]//text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )
                    city = " ".join(city.split())
                    if city.endswith(","):
                        city = "".join(city[:-1]).strip()
                    phone = (
                        "".join(
                            d.xpath(
                                './/span[@class="c-phone-number-span c-phone-main-number-span"]//text()'
                            )
                        )
                        or "<MISSING>"
                    )
                    r = session.get(page_url, headers=headers)
                    tree = html.fromstring(r.text)

                    latitude = (
                        "".join(tree.xpath('//meta[@itemprop="latitude"]/@content'))
                        or "<MISSING>"
                    )
                    longitude = (
                        "".join(tree.xpath('//meta[@itemprop="longitude"]/@content'))
                        or "<MISSING>"
                    )
                    ll = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
                    if ll:
                        try:
                            latitude = ll.split("coord=")[1].split(",")[0].strip()
                            longitude = (
                                ll.split("coord=")[1]
                                .split(",")[1]
                                .split("&")[0]
                                .strip()
                            )
                        except:
                            latitude, longitude = "<MISSING>", "<MISSING>"
                    latitude = latitude.strip() or "<MISSING>"
                    longitude = longitude.strip() or "<MISSING>"
                    hours_of_operation = (
                        " ".join(
                            tree.xpath(
                                '//div[@class="Nap-addressWrapper"]/following-sibling::div[@class="c-location-hours"]//table//tr//td//text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                    )
                    hours_of_operation = (
                        " ".join(hours_of_operation.split()) or "<MISSING>"
                    )
                    if hours_of_operation == "<MISSING>":
                        hours_of_operation = (
                            " ".join(tree.xpath('//div[@id="store_hours"]//p//text()'))
                            .replace("\n", "")
                            .strip()
                            or "<MISSING>"
                        )
                        hours_of_operation = (
                            " ".join(hours_of_operation.split()) or "<MISSING>"
                        )
                    if hours_of_operation.count("Closed") == 7:
                        hours_of_operation = "Closed"

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

    locator_domain = "https://earlofsandwichusa.com/"
    page_url = "https://locations.earlofsandwichusa.com/kr/seoul/653-16--sinsa-dong"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        " ".join(tree.xpath('//span[@class="LocationName"]//text()'))
        .replace("\n", "")
        .strip()
    )
    location_name = " ".join(location_name.split())
    street_address = "".join(
        tree.xpath(
            '//address[@id="address"]//span[@class="c-address-street-1 "]//text()'
        )
    )
    state = (
        "".join(
            tree.xpath(
                '//address[@id="address"]//span[@class="c-address-sublocality break-before"]//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    country_code = "KR"
    city = "".join(
        tree.xpath('//address[@id="address"]//span[@class="c-address-city "]//text()')
    )
    latitude = (
        "".join(tree.xpath('//meta[@itemprop="latitude"]/@content')) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath('//meta[@itemprop="longitude"]/@content')) or "<MISSING>"
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="Nap-addressWrapper"]/following-sibling::div[@class="c-location-hours"]//table//tr//td//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=SgRecord.MISSING,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
