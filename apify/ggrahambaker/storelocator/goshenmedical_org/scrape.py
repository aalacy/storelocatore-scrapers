import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import httpx

log = sglog.SgLogSetup().get_logger(logger_name="goshenmedical.org")


def fetch_data():

    locator_domain = "http://goshenmedical.org"
    api_url = "http://goshenmedical.org/allcounties.html"
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
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    }
    if True:
        timeout = httpx.Timeout(120.0, connect=120.0)
        with SgRequests(
            proxy_country="us",
            dont_retry_status_codes=([404]),
            timeout_config=timeout,
            retries_with_fresh_proxy_ip=20,
        ) as session:
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

                log.info(page_url)
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
                        " ".join(tree.xpath('//span[@class="sitename"]/text()'))
                        or "<MISSING>"
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
                            tree.xpath(
                                '//span[@class="sitename"]/following-sibling::text()[1]'
                            )
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
                zip = a.get("postal")
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

                hours_table = tree.xpath('//td[@class="white-text"]//table//tr')

                hours_list = []
                try:
                    days = hours_table[0].xpath("td")
                    times = hours_table[1].xpath("td")
                    for i, day in enumerate(days):
                        hours_list.append(
                            "".join(days[i].xpath(".//text()"))
                            .strip()
                            .replace("\n", "")
                            .strip()
                            + ": "
                            + "".join(times[i].xpath(".//text()"))
                            .strip()
                            .replace("\n", "")
                            .strip()
                        )
                except:
                    pass
                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .replace(
                        "Monday - Thursday                    7:00 - 6:00                      Closed Friday: Closed for Lunch                      Monday-Thursday 1-2 pm",
                        "Monday - Thursday: 7:00 - 6:00, Friday: Closed",
                    )
                )

                if hours_of_operation.find("*") != -1:
                    hours_of_operation = hours_of_operation.split("*")[0].strip()

                final_hours_list = []
                try:
                    temp_hours = hours_of_operation.split(";")
                    for hour in temp_hours:
                        try:
                            day = hour.split(":", 1)[0].strip()
                            temp_time = hour.split(":", 1)[1].strip().split("-")
                            time = temp_time[0].strip() + "-" + temp_time[1].strip()
                            final_hours_list.append(day + ":" + time)
                        except:
                            pass

                    hours_of_operation = "; ".join(final_hours_list).strip()
                except:
                    pass
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude="<MISSING>",
                    longitude="<MISSING>",
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
