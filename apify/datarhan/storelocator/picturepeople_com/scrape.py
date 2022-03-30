from lxml import etree
from requests_toolbelt import MultipartEncoder

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    DOMAIN = "picturepeople.com"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
    }
    import requests

    session = requests.Session()
    proxies = {"https": "127.0.0.1:24000", "http": "127.0.0.1:24000"}
    response = session.get(
        "https://tpp.mystratus.com/onlinebooking.aspx?loginoption=defaultnew",
        headers=headers,
        proxies=proxies,
        verify=False,
    )
    response = session.get(response.url, proxies=proxies, verify=False)
    response = session.get(
        "https://tpp.mystratus.com/22.05/OnlineBooking/verify.aspx?loginoption=defaultnew",
        proxies=proxies,
        verify=False,
    )
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    frm = {
        "__EVENTTARGET": "btnPageLoad",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewgen,
        "__EVENTVALIDATION": eventval,
        "hdnLoaded": True,
        "hdnTimeZone": "Europe/Madrid",
    }
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    response = session.post(
        response.url, proxies=proxies, data=frm, verify=False, headers=hdr
    )
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    hdr = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-",
        "Origin": "https://tpp.mystratus.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for code in all_codes:
        formdata = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewgen,
            "__EVENTVALIDATION": eventval,
            "txtLocationQuery": code,
            "cmbWithinDistance": "200",
            "btnLoadLocations": "Search",
        }

        me = MultipartEncoder(fields=formdata)
        me_boundary = me.boundary[2:]
        me_body = me.to_string()
        headers = {"Content-Type": "multipart/form-data; boundary=" + me_boundary}
        response = session.post(
            response.url, data=me_body, headers=headers, verify=False, proxies=proxies
        )
        dom = etree.HTML(response.text)
        viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

        all_locations = dom.xpath('//div[@class="LocationDiv"]')
        for poi_html in all_locations:
            location_name = poi_html.xpath('.//div[@class="StudioInfoClass"]/b/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = poi_html.xpath('.//div[@class="StudioInfoClass"]/text()')
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            phone = raw_address[-1] if zip_code not in raw_address[-1] else ""

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.picturepeople.com/book-a-session/",
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1].split()[0],
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation="",
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
