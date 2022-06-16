from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


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
        store_number = j.get("id")
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

        api_page_url = f"https://www.cocodimama.co.uk/wp-json/locations/get_venue_info_from_id?id={store_number}"
        r = session.get(api_page_url, headers=headers)
        js = r.json()["data"]
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = str(d).capitalize()
            opens = js.get(f"{d}_opening_times").get("open_time")
            closes = js.get(f"{d}_opening_times").get("close_time")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = (
            "; ".join(tmp).replace("closed - ", "closed").strip() or "<MISSING>"
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
            store_number=store_number,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
