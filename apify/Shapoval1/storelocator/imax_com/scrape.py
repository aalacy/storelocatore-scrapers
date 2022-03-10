import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures
from sglogging import sglog

locator_domain = "https://www.imax.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.imax.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):

    page_url = "".join(url)

    if page_url.count("/") != 4 or page_url.find("/theatres/") == -1:
        return
    log.info(f"Page URL: {page_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(page_url, headers=headers))
        log.info(f"## Response: {r}")

        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        js = json.loads(js_block)
        location_name = js.get("name")
        location_type = js.get("@type")
        ad = "".join(js.get("address"))
        a = parse_address(International_Parser(), ad)

        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address.find(" ") == -1:
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        states_us = [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DC",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
            "California",
            "Nevada",
            "Illinois",
            "Texas",
            "Indiana",
            "Iowa",
            "Virginia",
            "New York",
            "New Jersey",
            "Mississippi",
            "Michigan",
            "Wisconsin",
            "Colorado",
        ]
        state_ca = [
            "AB",
            "BC",
            "MB",
            "NB",
            "NL",
            "NT",
            "NS",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
            "Ontario",
        ]
        postal = a.postcode or "<MISSING>"
        country_code = a.country or "<MISSING>"
        if "40067-00100" in country_code:
            country_code = country_code.replace("40067-00100", "").strip()
            postal = "40067-00100"
        if state in states_us:
            country_code = "USA"
        if (
            "China" in ad
            or "CHN.GX" in ad
            or "CHN" in ad
            or "Ziyang" in ad
            or "Wenling" in ad
            or "Chongqing" in ad
            or "Shanxi" in ad
            or "Jiangsu" in ad
            or "Beijing" in ad
        ):
            country_code = "China"
        if state in state_ca:
            country_code = "CA"
        if "BRA" in ad:
            country_code = "Brazil"
        if "COL" in ad or "Columbia" in ad:
            country_code = "Columbia"
        if "Gyeonggi-do" in ad or "Korea" in ad or "Seoul" in ad:
            country_code = "Korea"
        if "Japan" in ad:
            country_code = "Japan"
        if "Mexico" in ad or "Aguascalientes" in ad or "Naucalpan de Juárez" in ad:
            country_code = "Mexico"
        if "RUS" in ad:
            country_code = "Russia"
        if "UAE" in ad:
            country_code = "UAE"
        if "Sweden" in ad:
            country_code = "Sweden"
        if "Qatar" in ad:
            country_code = "Qatar"
        if "Croatia" in ad:
            country_code = "Croatia"
        if "SE100QJ" in ad or "England" in ad or "Saskatchewan" in ad:
            country_code = "UK"
        if "Bangalore" in ad:
            country_code = "India"
        if "Ireland" in ad:
            country_code = "Ireland"
        if "Kyrgyzstan" in ad:
            country_code = "Kyrgyzstan"
        if "Greece" in ad:
            country_code = "Greece"
        if "Kuwait" in ad:
            country_code = "Kuwait"
        if "Panama" in ad:
            country_code = "Panama"
        if "Guayas" in ad:
            country_code = "Ecuador"
        if "Aruba" in ad:
            country_code = "Aruba"

        city = a.city or "<MISSING>"
        if street_address.find(" ") == -1:
            street_address = " ".join(ad.split(",")[:2]).strip()
        latitude = js.get("geo").get("latitude") or "<MISSING>"
        longitude = js.get("geo").get("longitude") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        if page_url == "https://www.imax.com/theatres/109-cinemas-futako-tamagawa-imax":
            city = "Setagayaku"
        if page_url == "https://www.imax.com/theatres/la-geode":
            city = "Paris"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)

    except Exception as e:
        log.info(f"Err at #L100: {e}")


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
