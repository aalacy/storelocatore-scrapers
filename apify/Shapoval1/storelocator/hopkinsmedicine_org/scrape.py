from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hopkinsmedicine.org/"
    api_url = "https://www.hopkinsmedicine.org/patient_care/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[./div[@class="card-content"]/div/h3]')
    for d in div:

        page_url = "".join(d.xpath(".//h3/a/@href"))
        location_name = "".join(d.xpath(".//h3/a/text()")).replace("\n", "").strip()
        if location_name.find("— ") != -1:
            location_name = location_name.split("— ")[0].strip()
        info = d.xpath('.//div[@class="details"]/text()')
        info = list(filter(None, [a.strip() for a in info]))
        for i in info:
            if "|" in i:
                info = info[:-1]

        location_type = (
            "".join(d.xpath(".//preceding::h2[1]//text()")).replace("\n", "").strip()
        )
        street_address = "".join(info[0]).strip()
        ad = "".join(info[-1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(d.xpath('.//div[@class="location-phone"]//a/text()')) or "<MISSING>"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone_lst = tree.xpath('//a[contains(@href, "tel")]/text()')
        phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
        if phone == "<MISSING>":
            phone = "".join(phone_lst[1]).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[@id="practice-hours"]/following-sibling::p[./strong[contains(text(), "Every")]][1]//text()'
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
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    locator_domain = "https://www.hopkinsmedicine.org"
    api_url = "https://www.hopkinsmedicine.org/community_physicians/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="card-link"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h2[@class="text-black"]/text()'))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("—") != -1:
            location_name = location_name.split("—")[0].strip()
        if not location_name:
            continue

        location_type = "Community Physicians Locations"
        info = tree.xpath(
            '//a[text()="Google Map"]/preceding-sibling::text() | //strong[contains(text(), "Community Physicians")]/following-sibling::text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        for i in info:
            if "|" in i:
                info = info[:-1]
        street_address = " ".join(info[:-1]).strip()
        ad = "".join(info[-1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        if location_name.find(f"{city}") != -1:
            location_name = location_name.split(f", {city}")[0].strip()
        phone_lst = tree.xpath('//a[contains(@href, "tel")]/text()')
        phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
        phone = "".join(phone_lst[1]).strip()
        if phone == "Call us":
            phone = "".join(phone_lst[3]).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//ul[@class="location-hours"]/li//text() | //h3[text()="Practice Hours"]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Appointment") != -1:
            hours_of_operation = hours_of_operation.split("Appointment")[0].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    locator_domain = "https://www.hopkinsmedicine.org/"
    api_url = "https://www.hopkinsmedicine.org/community_physicians/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="card-link"]')
    for d in div:
        page_url_sub = "".join(d.xpath(".//@href"))
        r = session.get(page_url_sub, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="content"]/h2[./a]/a')
        for d in div:

            page_url = "".join(d.xpath(".//@href"))
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = (
                "".join(tree.xpath('//h1[@class="article-title"]//text()'))
                .replace("\n", "")
                .strip()
            )
            if location_name.find("—") != -1:
                location_name = location_name.split("—")[0].strip()

            location_type = "Community Physicians Locations"
            info = tree.xpath(
                '//a[text()="Google Map"]/preceding-sibling::text() | //strong[contains(text(), "Community Physicians")]/following-sibling::text()'
            )
            info = list(filter(None, [a.strip() for a in info]))
            for i in info:
                if "|" in i:
                    info = info[:-1]
            street_address = " ".join(info[:-1]).strip()
            ad = "".join(info[-1]).strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            if location_name.find(f"{city}") != -1:
                location_name = location_name.split(f", {city}")[0].strip()
            phone_lst = tree.xpath('//a[contains(@href, "tel")]/text()')
            phone_lst = list(filter(None, [a.strip() for a in phone_lst]))
            phone = "".join(phone_lst[1]).strip()
            if phone == "Call us":
                phone = "".join(phone_lst[3]).strip()
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//ul[@class="location-hours"]/li//text() | //h3[text()="Practice Hours"]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .replace("\r", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation.find("Appointment") != -1:
                hours_of_operation = hours_of_operation.split("Appointment")[0].strip()
            if hours_of_operation.find("Due to") != -1:
                hours_of_operation = "<MISSING>"

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
