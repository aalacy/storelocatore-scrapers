import os
import ssl
from lxml import html
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-jp:{}@proxy.apify.com:8000/"

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

locator_domain = "https://www.yusen-logistics.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://www.yusen-logistics.com/about-us/find-an-office"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    try:
        r = SgRequests.raise_on_err(session.get(api_url, headers=headers))
        tree = html.fromstring(r.text)
        div = tree.xpath('//input[@name="field_office_region"]')[1:]
        for d in div:
            val = "".join(d.xpath(".//@value"))
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            }

            params = {
                "lock_config_key": "7o-QBrh_qGd1zik3OfcZYFb19yqImJnqBaECS4T-BQ0",
                "_wrapper_format": "drupal_ajax",
            }

            data = {
                "search_api_fulltext": "",
                "field_office_region": f"{val}",
                "view_name": "find_an_office",
                "view_display_id": "find_an_office",
                "view_args": "",
                "view_path": "/node/966",
                "view_query": "block_config_key=7o-QBrh_qGd1zik3OfcZYFb19yqImJnqBaECS4T-BQ0",
                "view_base_path": "",
                "view_dom_id": "c3606560cc5e3e4df9bf423b96710907978480f2d6b58894538a6ce575927669",
                "pager_element": "0",
                "_drupal_ajax": "1",
                "ajax_page_state[theme]": "yusen",
                "ajax_page_state[theme_token]": "",
                "ajax_page_state[libraries]": "bartik/classy.base,bartik/classy.messages,bartik/global-styling,better_exposed_filters/general,better_exposed_filters/select_all_none,ciandt_layout_discovery/grid_onecol_section,core/normalize,extlink/drupal.extlink,paragraphs/drupal.paragraphs.unpublished,system/base,views/views.ajax,views/views.module,yusen/main",
            }

            r = session.post(
                "https://www.yusen-logistics.com/views/ajax",
                params=params,
                headers=headers,
                data=data,
            )
            js = r.json()
            for j in js:

                dat = j.get("data")
                if not dat:
                    continue
                tree = html.fromstring(dat)
                div = tree.xpath('//div[./div[@class="office-item-info"]]')
                for d in div:

                    country_code = "".join(d.xpath(".//preceding::h3[1]//text()"))
                    page_url = "https://www.yusen-logistics.com/about-us/find-an-office"
                    location_name = (
                        "".join(
                            d.xpath('.//p[@class="office-item-info-city"]//text()')
                        ).strip()
                        or "<MISSING>"
                    )
                    location_type = (
                        ",".join(
                            d.xpath(
                                './/div[@class="office-item-info-facilities"]/span/text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )
                    ad = (
                        " ".join(
                            d.xpath(
                                './/div[@class="office-item-content-left"]/p[last()]//text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                    )
                    ad = " ".join(ad.split())
                    a = parse_address(International_Parser(), ad)
                    street_address = (
                        f"{a.street_address_1} {a.street_address_2}".replace(
                            "None", ""
                        ).strip()
                        or "<MISSING>"
                    )
                    if street_address == "<MISSING>" or street_address.isdigit():
                        street_address = ad
                    state = a.state or "<MISSING>"
                    postal = a.postcode or "<MISSING>"
                    postal = (
                        str(postal)
                        .replace("CP", "")
                        .replace("C.P.", "")
                        .replace("H-", "")
                        .replace("BUILD.2", "")
                        .replace("CH-", "")
                        .replace("LAHORE.3", "")
                        .replace(".", "")
                        .replace("BLDG", "")
                        .strip()
                        or "<MISSING>"
                    )
                    city = a.city or "<MISSING>"
                    if country_code == "India" and str(postal).find("-") != -1:
                        city = str(postal).split("-")[0].strip()
                        postal = str(postal).split("-")[1].strip()
                    if country_code == "India" and str(city).find("-") != -1:
                        postal = str(city).split("-")[1].strip()
                        city = str(city).split("-")[0].strip()
                    text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
                    try:
                        latitude = text.split("q=")[1].split(",")[0].strip()
                        longitude = text.split("q=")[1].split(",")[1].strip()
                    except IndexError:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                    phone = (
                        "".join(
                            d.xpath(
                                './/span[contains(text(), "TEL:")]/following-sibling::*[1]//text()'
                            )
                        )
                        .replace("\n", "")
                        .replace("(Auto 30 Lines)", "")
                        .strip()
                        or "<MISSING>"
                    )
                    if phone.find("(Export)") != -1:
                        phone = phone.split("(Export)")[0].strip()
                    if phone.count("(420)") > 1:
                        phone = "(420)" + phone.split("(420)")[1].strip()
                    if phone.find("(Sales)") != -1 and phone.find("(Main Line)") != -1:
                        phone = phone.split("(Sales)")[0].strip()
                    if (
                        phone.find("(Logistics)") != -1
                        and phone.find("(Ocean Export & Import)") != -1
                    ):
                        phone = phone.split("(Logistics)")[0].strip()
                    if phone.find("(Air Export) ") != -1:
                        phone = phone.split("(Air Export) ")[0].strip()
                    if phone.find("(Main Line)") != -1:
                        phone = phone.split("(Main Line)")[0].strip()
                    if phone.find("(Air)") != -1:
                        phone = phone.split("(Air)")[0].strip()
                    if phone.count("92 42") > 1:
                        phone = phone.split("+92 42")[0].strip()
                    if phone.count("951-") > 1:
                        phone = "951-" + phone.split("951-")[1].strip()
                    if phone.count("(880)-") > 1:
                        phone = "(880)-" + phone.split("(880)-")[1].strip()

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
