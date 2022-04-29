import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()

headers = {
    "authority": "www.belowthebelt.com",
    "method": "GET",
    "path": "/pages/stores-json",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cookie": 'secure_customer_sig=; localization=US; cart_currency=USD; _orig_referrer=; _landing_page=%2F; _y=f6cf9a4a-e525-4936-8817-bab76a2bf152; _shopify_y=f6cf9a4a-e525-4936-8817-bab76a2bf152; _ga=GA1.2.1367774872.1646646103; _gid=GA1.2.1130251005.1646646103; _gcl_au=1.1.1690215516.1646646105; _fbp=fb.1.1646646105366.1837267236; locale_bar_accepted=1; soundestID=20220307094151-48MqeyeO6ZrdC5APAX9qZOru8qfzrqasZYpcduv7wBmkdGrJG; omnisendAnonymousID=jR8ERNrAFcXdHg-20220307094151; _s=59e4badc-3d1d-43a2-93b7-1a6e13c87088; _shopify_s=59e4badc-3d1d-43a2-93b7-1a6e13c87088; _shopify_sa_p=; _gat=1; shopify_pay_redirect=pending; swym-session-id="qznhta0tzy8y5xz3amdqrkg4y3fq1exwg3mifzksuya56qe6jbsmyb7114qs95n1"; omnisendSessionID=7asg5i6XhS8i1p-20220307132351; soundest-views=9; _shopify_sa_t=2022-03-07T13%3A23%3A57.614Z',
    "referer": "https://www.belowthebelt.com/pages/store-locator",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():

    url = "https://www.belowthebelt.com/pages/stores-json"
    r = session.get(url, headers=headers)

    content = r.text.split(' "stores": ', 1)[1].split("]", 1)[0]
    content = content + "]"
    loclist = json.loads(content.strip())
    for loc in loclist:

        title = loc["Fcilty_nam"]
        street = loc["Street_add"]
        try:
            city, pcode = loc["Locality"].split(", ", 1)
            state = loc["Postcode"]
        except:
            street = street + " " + loc["Locality"]
            city, pcode, state = loc["Postcode"].split(",", 2)
        phone = loc["Phone_number"]
        lat = loc["Ycoord"]
        longt = loc["Xcoord"]

        yield SgRecord(
            locator_domain="https://www.belowthebelt.com/",
            page_url="https://www.belowthebelt.com/pages/store-locator",
            location_name=title,
            street_address=street.replace("<span>", "").replace("</span>", "").strip(),
            city=city.replace("<span>", "").replace("</span>", "").strip(),
            state=state.replace("<span>", "").replace("</span>", "").strip(),
            zip_postal=pcode.replace("<span>", "").replace("</span>", "").strip(),
            country_code="CA",
            store_number=SgRecord.MISSING,
            phone=phone.replace("<span>", "").replace("</span>", "").strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation="<MISSING>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
