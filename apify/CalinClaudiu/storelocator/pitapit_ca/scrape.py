from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="pita*2")


def parse_soup(soup, url):
    page_url = SgRecord.MISSING
    location_name = SgRecord.MISSING
    street_address = SgRecord.MISSING
    city = SgRecord.MISSING
    state = SgRecord.MISSING
    zip_postal = SgRecord.MISSING
    country_code = SgRecord.MISSING
    store_number = SgRecord.MISSING
    phone = SgRecord.MISSING
    location_type = SgRecord.MISSING
    latitude = SgRecord.MISSING
    longitude = SgRecord.MISSING
    hours_of_operation = SgRecord.MISSING
    raw_address = SgRecord.MISSING

    page_url = url
    try:
        location_name = soup.find(
            "div",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-title",
                        "title",
                        "fusion-title-1",
                        "fusion-sep-none",
                        "fusion-title-text",
                        "fusion-title-size-one",
                    ]
                )
            },
        )
        location_name = location_name.find("h1").text.strip()
    except Exception:
        pass

    try:
        raw_address = soup.find(
            "div",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-layout-column",
                        "fusion_builder_column",
                        "fusion-builder-column-14",
                        "fusion_builder_column_1_2",
                        "1_2",
                        "fusion-flex-column",
                    ]
                )
            },
        )
        raw_address = " ".join(list(raw_address.find("p").stripped_strings))
    except Exception:
        pass
    parsed = parser.parse_address_intl(raw_address)
    try:
        street_address = (
            parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        )
        street_address = (
            (street_address + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street_address
        )
        city = parsed.city if parsed.city else SgRecord.MISSING
        state = parsed.state if parsed.state else SgRecord.MISSING
        zip_postal = parsed.postcode if parsed.postcode else SgRecord.MISSING
        country_code = parsed.country if parsed.country else SgRecord.MISSING
    except Exception as e:
        logzilla.error("", exc_info=e)
        pass

    try:
        store_number = soup.find(
            "a",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-button",
                        "button-flat",
                        "fusion-button-default-size",
                        "button-custom",
                        "button-8",
                        "fusion-button-span-no",
                        "fusion-button-default-type",
                        "transparent-btn-icon",
                    ]
                )
            },
        )
        store_number = store_number.find("span").text.strip()
        store_number = store_number.split("@", 1)[0]
    except Exception:
        pass
    try:
        phone = soup.find(
            "a",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-button",
                        "button-flat",
                        "fusion-button-default-size",
                        "button-custom",
                        "button-7",
                        "fusion-button-span-no",
                        "fusion-button-default-type",
                        "transparent-btn-icon",
                    ]
                )
            },
        )
        phone = phone.find("span").text.strip()
    except Exception:
        pass

    def hoursB(soup, column):
        hours_of_operation = soup.find(
            "div",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-layout-column",
                        "fusion_builder_column",
                        f"fusion-builder-column-{str(column)}",
                        "fusion_builder_column_1_2",
                        "1_2",
                        "fusion-flex-column",
                    ]
                )
            },
        )

        hours_of_operation = hours_of_operation.find_all("p")
        temphr = []
        for i in hours_of_operation:
            if "day" in i.text:
                block = ""
                block = i.text.strip()
                block = block + " "
            if any(z.isdigit() for z in i.text) or "osed" in i.text:
                block = block + "- "
                block = block + i.text.strip()
                temphr.append(block)
                block = ""
        return ", ".join(temphr)

    try:
        hours_of_operation = hoursB(soup, 16)
    except Exception:
        try:
            hours_of_operation = hoursB(soup, 15)
        except Exception as e:
            logzilla.error("", exc_info=e)

    try:

        def parse_coords(gMapUrl):
            gMapUrl = list(gMapUrl)
            try:
                gMapUrl = gMapUrl[57:]
            except Exception:
                try:
                    gMapUrl = gMapUrl[38:]
                except Exception:
                    pass
            longitude = []
            latDone = False
            lngDone = False
            latitude = []
            while gMapUrl:
                i = gMapUrl.pop(-1)
                if not latDone:
                    if i.isdigit():
                        latitude.insert(0, i)
                        continue
                    if i == ".":
                        latitude.insert(0, i)
                        latDone = "close"
                        continue
                if latDone == "close":
                    if i.isdigit() or i == "-":
                        latitude.insert(0, i)
                        continue
                    else:
                        latDone = True
                if not lngDone:
                    if i.isdigit():
                        longitude.insert(0, i)
                        continue
                    if i == ".":
                        longitude.insert(0, i)
                        lngDone = "close"
                        continue
                if lngDone == "close":
                    if i.isdigit() or i == "-":
                        longitude.insert(0, i)
                        continue
                    else:
                        lngDone = True
                        continue
            if all([latDone, lngDone]):
                if longitude[0] == "-":
                    return ("".join(latitude), "".join(longitude))
                return ("".join(longitude), "".join(latitude))
            return (SgRecord.MISSING, SgRecord.MISSING)

        links = soup.find_all(
            "a",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-button",
                        "button-flat",
                        "fusion-button-default-size",
                        "button-custom button-6",
                        "button-6",
                        "fusion-button-span-no",
                    ]
                )
            },
        )
        for link in links:
            if "irection" in link.find("span").text.strip():
                latitude, longitude = parse_coords(link["href"])
    except Exception as e:
        logzilla.error("", exc_info=e)
        raise
    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain="https://pitapit.ca/",
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )


def fetch_data(sess):
    def search_api(session):
        url = "https://pitapit.ca/locations/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
        }

        resp = SgRequests.raise_on_err(session.get(url, headers=headers))
        soup = b4(resp.text, "lxml")
        links = soup.find_all(
            "a",
            {
                "class": lambda x: x
                and all(
                    i in x
                    for i in [
                        "fusion-button",
                        "button-flat",
                        "fusion-button-default-size",
                        "button-custom",
                        "fusion-button-span-no",
                        "fusion-button-default-type",
                    ]
                ),
                "href": True,
            },
        )

        for link in links:
            if "https://pitapit.ca/restaurants/" in link["href"]:
                yield link["href"]

    def fetch_sub(session, url):
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
        resp = SgRequests.raise_on_err(session.get(url, headers=headers))
        soup = b4(resp.text, "lxml")
        return parse_soup(soup, url)

    for result in search_api(sess):
        k = fetch_sub(sess, result)
        yield k


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_data(http):
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
