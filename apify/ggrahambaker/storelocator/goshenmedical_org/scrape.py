import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "http://goshenmedical.org"
    api_url = "http://goshenmedical.org/allcounties.html"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//a[./img]")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        if slug.find("/") == -1:
            slug = "/" + slug
        page_url = f"http://www.goshenmedical.org{slug}"
        if page_url.find(" ") != -1:
            page_url = page_url.replace(" ", "%20")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(
                tree.xpath(
                    '//span[@class="siteaddress"]/preceding-sibling::span//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                " ".join(tree.xpath('//span[@class="sitename"]/text()')) or "<MISSING>"
            )
        if location_name.find("Providers") != -1:
            location_name = (
                location_name.split("Providers")[0]
                .replace("\r\n", "")
                .replace("\n", "")
                .strip()
            )
        if page_url == "http://www.goshenmedical.org/raeford.html":
            location_name = "Goshen Medical Center, Raeford"
        ad = (
            " ".join(tree.xpath('//*[@class="siteaddress"]//text()'))
            .replace("\n", " ")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath('//span[@class="sitename"]/following-sibling::text()[1]')
                )
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
        ad = (
            ad.replace("(formerly Sampson Medical Services PA)", "")
            .replace("·", "")
            .replace(" - ", " ")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        phone = (
            "".join(
                tree.xpath(
                    '//strong[.//text()="Phone Number"]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if page_url == "http://www.goshenmedical.org/clinton-medical.html":
            phone = "(910) 592-1462"
        with SgFirefox() as fox:
            fox.get(page_url)
            fox.implicitly_wait(5)
            hours_table = fox.find_element_by_css_selector(
                "td.white-text"
            ).find_element_by_css_selector("table")

            rows = hours_table.find_elements_by_css_selector("tr")

            days = rows[0].find_elements_by_css_selector("td")
            times = rows[1].find_elements_by_css_selector("td")
            hours = ""
            for i, day in enumerate(days):
                hours += days[i].text + " " + times[i].text + " "

            if len(rows) > 2:
                extra = rows[2].text
                hours += extra

            hours_of_operation = " ".join(hours.split())
            if hours_of_operation.find("*") != -1:
                hours_of_operation = hours_of_operation.split("*")[0].strip()

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
    locator_domain = "https://www.1stbmt.com"
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        fetch_data(writer)
