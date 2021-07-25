import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = (
        "https://www.lesaint.com/warehouse-ecommerce-fulfillment-centers-locations/"
    )
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
    div = tree.xpath('//section[@class="zn_section eluid8c9d7270     section-sidemargins    section--no "]//div[./p/a]')

    for d in div:
        ad = d.xpath('.//p//text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = " ".join(ad).replace("Get Directions", "").replace("OH,", "OH").replace("Boulevard,", "Boulevard").replace("6044 0", "60440")
        if ad.find("TAGG Logistics") != -1:
            ad = ad.split("TAGG Logistics")[1].strip()
        if ad.count(",") == 2:
            ad = " ".join(ad.split(",")[1:]).split()[1:]
            ad = " ".join(ad)
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_name = "".join(d.xpath('.//span[@class="location-name"]/text() | .//span[./strong]/strong/text() | .//span[./a]/a/text() | .//a[./span]/span/text()'))
        if ad.find("13204 ") != -1:
            location_name = "Los Angeles, CA"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace('None','').strip()
        state = a.get('state') or '<MISSING>'
        postal = a.get('postal') or '<MISSING>'
        country_code = "US"
        city = a.get('city') or '<MISSING>'
        page_url = ''.join(d.xpath('.//a[contains(@href, "tagglogistics")]/@href')) or '<MISSING>'
        if page_url.count('https') == 2:
            page_url = ''.join(d.xpath('./p/a[contains(@href, "tagglogistics")][1]/@href')) or '<MISSING>'
        if page_url == '<MISSING>':
            page_url = ''.join(d.xpath('.//a[contains(@href, "order-fulfillment")]/@href')).replace('/order','order').replace('..','') or '<MISSING>'
        if page_url.find('https') == -1 and page_url != '<MISSING>':
            page_url = f'https://www.lesaint.com/{page_url}'
        if page_url == '<MISSING>':
            page_url = ''.join(d.xpath('.//p/span[1]/a/@href')).replace('..','') or '<MISSING>'
        if page_url.find('https') == -1 and page_url != '<MISSING>':
            page_url = f"https://www.lesaint.com{page_url}"
        page_url = page_url.replace('<MISSING>','') or 'https://www.lesaint.com/warehouse-ecommerce-fulfillment-centers-locations/'
        text = ''.join(d.xpath('.//a[contains(text(), "Get")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        if page_url.find("tagglogistics") != -1:
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            phone = " ".join(tree.xpath("//*//strong/a/text()")).split()[0].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.lesaint.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
