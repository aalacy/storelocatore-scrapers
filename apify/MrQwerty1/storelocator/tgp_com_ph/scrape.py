import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    part = line.split()[-1]
    if part.isdigit():
        adr = parse_address(International_Parser(), line, postcode=part)
    else:
        adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state or ""
    postal = adr.postcode or ""

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://tgp.com.ph/wp-admin/admin-ajax.php"
    r = session.post(api, headers=headers, data=data)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations')]/text()"))
    text = text.split('"locations":')[1].split(',"unit"')[0]
    js = json.loads(text)

    for j in js:
        source = j.get("infowindow") or "<html/>"
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        raw_address = "".join(
            d.xpath(".//p[@class='info-window-address']//text()")
        ).strip()

        # Clean spaces from raw address.
        raw_address = " ".join(raw_address.split())

        street_address = ""
        sta, city, state, postal = get_international(raw_address)

        # Postal address found in street address after parsing
        # using our parser, therefore, cleaning street address
        # and making it INACCESSIBLE if it is found to be empty.
        if postal in sta:
            street_address = sta.replace(postal, "").strip().rstrip()
        else:
            street_address = sta
        street_address = street_address if street_address else "<INACCESSIBLE>"
        city = city if city else "<INACCESSIBLE>"
        state = state if state else "<INACCESSIBLE>"
        postal = postal if postal else "<INACCESSIBLE>"

        # Custom Street Address and City.
        if raw_address == "34 Bayanihan Village Lalud Calapan City Or Mindoro 5200":
            street_address = "34 Bayanihan Village"
        if raw_address == "1116 Parada Santa Maria Bulacan 3023":
            street_address = "1116 Parada Santa Maria"
        if raw_address == "277 Brgy, Muzon City Of San Jose Del Monte, Bulacan 3023":
            street_address = "277 Brgy"
        if raw_address == "04 Maria Aurora Aurora 3202":
            street_address = "04 Maria Aurora"
        if raw_address == "0952 Sta. Rosa I, Marilao Bulacan 3019":
            street_address = "0952 Sta. Rosa I"
        if raw_address == "229 Francisco Tagaytay City Cavite 4120":
            street_address = "229 Francisco"
        if raw_address == "18 Kaytitinga 1 Alfonso Cavite 4123":
            street_address = "18 Kaytitinga 1"
        if (
            raw_address
            == "154 Libis Espina St Dagat Dagatan Brgy 016 Dist 2 Caloocan City"
        ):
            street_address = "154 Libis Espina St Dagat Dagatan Brgy 016 Dist 2"
        if (
            raw_address
            == "Blk 1 Lot 10 Marcos Alvarez Ave Veraville Townhomes Classic Talon V Las Pinas City 1740"
        ):
            city = "Las Pinas"
            street_address = "Blk 1 Lot 10 Marcos Alvarez Ave"
            city == ""
        if (
            raw_address
            == "No. 8 Centro St., Brgy. Lawang Bato, Dist. 1, Valenzuela City 1447"
        ):
            city = "Valenzuela City"
            street_address = "No. 8 Centro St."

        phone = "".join(d.xpath(".//p[./i[contains(@class, 'phone')]]/text()")).strip()
        if ";" in phone:
            phone = phone.split(";")[0].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="PH",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://tgp.com.ph/"
    page_url = "https://tgp.com.ph/branches/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://tgp.com.ph/branches/",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://tgp.com.ph",
        "Alt-Used": "tgp.com.ph",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "store_locatore_search_lat": "14.4976517",
        "store_locatore_search_lng": "121.0355912",
        "store_locatore_search_radius": "5000",
        "store_locator_category": "",
        "map_id": "997",
        "action": "make_search_request_custom_maps",
        "lat": "14.4976517",
        "lng": "121.0355912",
    }

    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
