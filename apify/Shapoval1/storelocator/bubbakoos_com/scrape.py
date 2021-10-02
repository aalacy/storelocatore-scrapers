import usaddress
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bubbakoos.com/"
    api_url = "https://www.bubbakoos.com/locations"
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
    with SgFirefox() as driver:
        driver.get(api_url)
        a = driver.page_source

        tree = html.fromstring(a)
        div = tree.xpath('//div[@class="location_part my-3"]')
        for d in div:
            slug = "".join(d.xpath(".//h3/a/@href"))
            page_url = f"https://www.bubbakoos.com/{slug}"
            location_name = "".join(d.xpath(".//h3/a/text()"))
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
            with SgFirefox() as driver:
                driver.get(page_url)
                driver.implicitly_wait(20)
                driver.maximize_window()
                driver.switch_to.frame(0)

                try:
                    ad = driver.find_element_by_xpath('//div[@class="address"]').text
                    ll = driver.find_element_by_xpath(
                        '//div[@class="google-maps-link"]/a'
                    ).get_attribute("href")
                except:
                    ad = "<MISSING>"
                    ll = "<MISSING>"
                ll = "".join(ll)
                ad = "".join(ad)

                driver.switch_to.default_content()
                a = usaddress.tag(ad, tag_mapping=tag)[0]
                street_address = (
                    f"{a.get('address1')} {a.get('address2')}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                city = a.get("city") or "<MISSING>"
                state = a.get("state") or "<MISSING>"
                postal = a.get("postal") or "<MISSING>"
                country_code = "US"
                try:
                    latitude = ll.split("ll=")[1].split(",")[0].strip()
                    longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"

                hours = driver.find_elements_by_xpath("//p[./span]/span")
                tmp = []
                for h in hours:
                    line = "".join(h.text).replace("\n", "").strip()
                    tmp.append(line)
                hours_of_operation = " ".join(tmp)
                if street_address == "<MISSING>":
                    ad = driver.find_element_by_xpath(
                        '//h3[./strong[contains(text(), "BUBBAKOO’S BURRITOS")]]/following-sibling::p[1]'
                    ).text
                    adr = driver.find_element_by_xpath(
                        '//h3[./strong[contains(text(), "BUBBAKOO’S BURRITOS")]]/following-sibling::p[2]'
                    ).text
                    adrp = driver.find_element_by_xpath(
                        '//h3[./strong[contains(text(), "BUBBAKOO’S BURRITOS")]]/following-sibling::p[4]'
                    ).text
                    city = "".join(ad).split(",")[0]
                    state = "".join(ad).split(",")[1]
                    street_address = "".join(adr)
                    postal = "".join(adrp)

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
