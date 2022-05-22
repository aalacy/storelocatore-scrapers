from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("days")
        opens = h.get("hours").get("open")
        closes = h.get("hours").get("close")
        line = f"{day} {opens}-{closes}"
        tmp.append(line)
        if opens == closes:
            line = f"{day} Closed"
            tmp.append(line)
    hours_of_operation = ";".join(tmp).replace("-;", "Closed;")
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://signaturestyle.com/brands/saturdays.html"
    api_url = "https://www.signaturestyle.com/salon-directory.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@href, "locations")]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        spage_url = f"https://www.signaturestyle.com{slug}"
        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath("//td[./a]")
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            page_url = f"https://www.signaturestyle.com{slug}"
            if (
                page_url
                == "https://www.signaturestyle.com/locations/ct/west-hartford/cost-cutters-cross-roads-plaza-haircuts-16888.html"
                or page_url
                == "https://www.signaturestyle.com/locations/wi/monroe/cost-cutters-located-inside-walmart-802-haircuts-17553.html"
            ):
                continue

            r = session.get(page_url, headers=headers)
            if r.status_code != 200:
                continue
            tree = html.fromstring(r.text)
            street_address = (
                "".join(
                    tree.xpath(
                        '//div[@class="salon-address loc-details-edit"]//span[@itemprop="streetAddress"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "".join(
                    tree.xpath(
                        '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="streetAddress"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                street_address = (
                    "".join(
                        tree.xpath(
                            '//p[@itemprop="address"]//span[@itemprop="streetAddress"]//text()'
                        )
                    )
                    or "<MISSING>"
                )

            city = (
                "".join(
                    tree.xpath(
                        '//div[@class="salon-address loc-details-edit"]//span[@itemprop="addressLocality"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "".join(
                    tree.xpath(
                        '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="addressLocality"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if city == "<MISSING>":
                city = (
                    "".join(
                        tree.xpath(
                            '//p[@itemprop="address"]//span[@itemprop="addressLocality"]//text()'
                        )
                    )
                    or "<MISSING>"
                )
            state = (
                "".join(
                    tree.xpath(
                        '//div[@class="salon-address loc-details-edit"]//span[@itemprop="addressRegion"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "".join(
                    tree.xpath(
                        '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="addressRegion"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if state == "<MISSING>":
                state = (
                    "".join(
                        tree.xpath(
                            '//p[@itemprop="address"]//span[@itemprop="addressRegion"]//text()'
                        )
                    )
                    or "<MISSING>"
                )
            postal = (
                "".join(
                    tree.xpath(
                        '//div[@class="salon-address loc-details-edit"]//span[@itemprop="postalCode"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "".join(
                    tree.xpath(
                        '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="postalCode"]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if postal == "<MISSING>":
                postal = (
                    "".join(
                        tree.xpath(
                            '//p[@itemprop="address"]//span[@itemprop="postalCode"]//text()'
                        )
                    )
                    or "<MISSING>"
                )
            country_code = "CA"
            if postal.isdigit():
                country_code = "US"
            store_number = page_url.split("-")[-1].split(".html")[0].strip()

            location_name = "".join(
                tree.xpath(
                    '//div[@class="salon-address loc-details-edit"]//div[@class="h2 h3"]/text()'
                )
            ).replace("\n", "").strip() or "".join(
                tree.xpath('//h1[@class="hidden-xs salontitle_salonsmalltxt"]/text()')
            )
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="salon-address loc-details-edit"]//span[@itemprop="telephone"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "".join(
                    tree.xpath(
                        '//div[@class="maps-container"]/following-sibling::div[3]//span[@itemprop="telephone"]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone == "<MISSING>":
                phone = (
                    "".join(
                        tree.xpath(
                            '//p[@itemprop="address"]/following-sibling::span[1]//text()'
                        )
                    )
                    or "<MISSING>"
                )
            try:
                latitude = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "salonDetailLat ")]/text()'
                        )
                    )
                    .split('salonDetailLat = "')[1]
                    .split('"')[0]
                )
                longitude = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "salonDetailLat ")]/text()'
                        )
                    )
                    .split('salonDetailLng = "')[1]
                    .split('"')[0]
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            location_type = "".join(
                tree.xpath(
                    '//div[@class="salon-address loc-details-edit"]//small[@class="sub-brand"]/text()'
                )
            )
            if "hairmasters" in page_url:
                location_type = "Hairmasters"
            if "island-haircutting" in page_url:
                location_type = "Island Haircutting"
            if "first-choice" in page_url:
                location_type = "First Choice"
            if "cost-cutters" in page_url:
                location_type = "Cost Cutters"
            if "holiday-hair" in page_url:
                location_type = "Holiday Hair"
            if "famous-hair" in page_url:
                location_type = "Famous Hair"
            if "tgf-hair" in page_url:
                location_type = "TGF"
            if "city-looks" in page_url:
                location_type = "City Looks"
            if "saturdays" in page_url:
                location_type = "Saturdays"
            if "head-start" in page_url:
                location_type = "Head Start"
            if "style-america" in page_url:
                location_type = "Style America"

            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="salon-timings displayNone"]/span//text() | //div[@class="maps-container"]/following-sibling::div[3]//div[@class="store-hours sdp-store-hours"]/span//span//text() | //div[@class="store-hours sdp-store-hours"]/span/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                jsurl = f"https://info3.regiscorp.com/salonservices/siteid/5/salon/{store_number}"
                r = session.get(jsurl, headers=headers)
                js = r.json()
                hours = js.get("store_hours") or "<MISSING>"
                hours_of_operation = "<MISSING>"
                if hours != "<MISSING>":
                    hours_of_operation = get_hours(hours)
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "Closed"
                if hours_of_operation.count("Closed") > 7:
                    hours_of_operation = "Closed"
                if hours_of_operation.count("Closed") == 6:
                    hours_of_operation = "Closed"
                if (
                    hours_of_operation
                    == "Monday-Friday Closed Saturday Closed Sunday Closed"
                ):
                    hours_of_operation = "Closed"
            if hours_of_operation.find("Mon Closed;Mon Closed;") != -1:
                hours_of_operation = hours_of_operation.replace(
                    "Mon Closed;Mon Closed;", "Mon Closed"
                )
            if hours_of_operation.find("Sun Closed;Sun Closed") != -1:
                hours_of_operation = hours_of_operation.replace(
                    "Sun Closed;Sun Closed", "Sun Closed"
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
