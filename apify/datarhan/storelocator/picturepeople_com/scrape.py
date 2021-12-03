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
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(
        "https://tpp.mystratus.com/21.13/OnlineBooking/verify.aspx?loginoption=defaultnew"
    )
    session_id = response.url.path.split("S(")[-1].split("))")[0]
    response = session.get(
        f"https://tpp.mystratus.com/21.13/(S({session_id}))/OnlineBooking/LocationSelection.aspx?loginoption=defaultnew",
        headers=headers,
    )
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    formdata = {
        "__EVENTTARGET": "redirect",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewgen,
        "__EVENTVALIDATION": eventval,
    }

    response = session.post(response.url, data=formdata, headers=headers)
    response = session.get(response.url, headers=headers)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    formdata = {
        "__EVENTTARGET": "btnPageLoad",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewgen,
        "__EVENTVALIDATION": eventval,
        "hdnLoaded": "true",
        "hdnTimeZone": "Europe/Madrid",
    }
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    response = session.post(response.url, data=formdata, headers=hdr)
    response = session.get(response.url, headers=headers)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]

    all_locations = []
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
        headers = {
            "Content-Type": "multipart/form-data; charset=utf-8; boundary="
            + me_boundary
        }

        response = session.post(response.url, data=me_body, headers=headers)
        dom = etree.HTML(response.text)
        viewstate = dom.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        viewgen = dom.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        eventval = dom.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]
        all_locations += dom.xpath('//div[@class="LocationDiv"]')

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="StudioInfoClass"]/b/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="StudioInfoClass"]/text()')
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        phone = raw_address[-1] if zip_code not in raw_address[-1] else SgRecord.MISSING

        item = SgRecord(
            locator_domain=DOMAIN,
            page_url="",
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
