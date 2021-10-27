from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cocodimama.co.uk/"
    api_url = "https://www.cocodimama.co.uk/wp-json/locations/get_venues"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        ad = "".join(j.get("address")).replace("\r\n", " ").replace("\n", " ").strip()
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or j.get("region") or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        page_url = "".join(j.get("link"))
        if page_url == "https://www.cocodimama.co.uk/locations/london-cheapside":
            street_address = ad.split(",")[0].strip()
        if (
            page_url == "https://www.cocodimama.co.uk/locations/bradford"
            or page_url
            == "https://www.cocodimama.co.uk/locations/glasgow-port-dundas-delivery-kitchen"
        ):
            postal = ad.split(",")[-1].strip()
        if (
            page_url
            == "https://www.cocodimama.co.uk/locations/glasgow-port-dundas-delivery-kitchen"
        ):
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            postal = ad.split(",")[-1].strip()
        if page_url == "https://www.cocodimama.co.uk/locations/lincoln":
            street_address = " ".join(ad.split(",")[:2]).strip()
            city = ad.split(",")[2].strip()
            postal = ad.split(",")[-1].strip()
        if page_url == "https://www.cocodimama.co.uk/locations/romford":
            street_address = " ".join(ad.split(",")[:2]).strip()
            city = ad.split(",")[3].strip()
            postal = ad.split(",")[-1].strip()
        if city == "Rushden Lakes Rushden":
            city = "Rushden"
        if page_url == "https://www.cocodimama.co.uk/locations/stratford-westfield":
            street_address = " ".join(ad.split(",")[:2]).strip()
            city = ad.split(",")[3].strip()
            postal = ad.split(",")[-1].strip()
        if page_url == "https://www.cocodimama.co.uk/locations/sutton":
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            postal = ad.split(",")[-1].strip()
        if page_url == "https://www.cocodimama.co.uk/locations/windsor":
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[1].strip()
            postal = ad.split(",")[-1].strip()
        if postal.find("Glasgow") != -1:
            postal = postal.replace("Glasgow", "").strip()
        if city.find("G2 3LD") != -1:
            city = city.replace("G2 3LD", "").strip()
        if (
            page_url
            == "https://www.cocodimama.co.uk/locations/leeds-birstall-delivery-kitchen"
        ):
            street_address = ad.split(",")[0].strip()
            city = ad.split(",")[2].strip()
            postal = ad.split(",")[-1].strip()
        location_name = j.get("title")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone_number") or "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        openToday = (
            " ".join(tree.xpath('//p[@class="c-opening-times__today"]/span/text()'))
            .replace("\n", "")
            .strip()
        )
        openToday = " ".join(openToday.split())

        openingTime = (
            " ".join(
                tree.xpath(
                    '//div[@class="c-opening-times__tables-holder"]//table//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        openingTime = " ".join(openingTime.split())
        hours_of_operation = openToday + " " + openingTime

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
