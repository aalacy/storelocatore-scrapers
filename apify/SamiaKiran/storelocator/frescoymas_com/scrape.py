import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "frescoymas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "cookie": 'SC_ANALYTICS_GLOBAL_COOKIE=00f32aa0ba9f4424954be13e40dea514|False; _gcl_au=1.1.1814903974.1611943994; _fbp=fb.1.1611943993886.797477434; _ga=GA1.2.1425035501.1611943994; _abck=77BA33D9299DB7782F21CA0A7E823FE0~0~YAAQTkwQArVuKkt3AQAAP31ZTwW7J5BzZHGQEluVQ56FtBSIRKNqZ96FhYAKLFVVIqPm583pdwWvxA1Vi8689IY+Hnm3bQJkLlVxC+VpltIGgIUQJg7nXCEhhcYwodE+2LWR0oQF6v+3njGt2++4shEiH0Be8/QNlAYHj0vZdasB59Ht35eTZt1R0XZTpddvQl4Aw0DgnhHMP8TCbtTWz3h399iAm9Bix3e3hgrC36JH8zzOManxLx0d7inisevD8plR41vre8iAf/YKSsQRObq/O7OXvpB7ieAVpgTll4ag2aq0PeL6Pt+pUG7GGOFur4buirjqH2mGhmq+fw/1LMCbamJ+Nf8VZIM=~-1~||-1||~-1; CookieBar=cookiebar; AKA_A2=A; ASP.NET_SessionId=3ejylqj2zhbltema1rc4ofd4; __RequestVerificationToken=5H15A9w0AKoy7hVr0cDszPkuSHsusvk_1NmhAS4EkHGFoo8wFmKvZgtCs1o2pt-yubIiz446_cr9-b3RSxb1l6sA1Swm-v511MaEW6ySogU1; sxa_site=websitefrescoymas1; ARRAffinity=f13f566f9bc83ce421b6c18067adc9b0f673c2a420185461f14ee771bab071f2; ARRAffinitySameSite=f13f566f9bc83ce421b6c18067adc9b0f673c2a420185461f14ee771bab071f2; ak_bmsc=4042CE84805DAECB2FD945496975EE2F02104C4EAD0C0000C3381860C099C41D~plc3sWe8Dyq8DwLLrZhjswU4Xgdx9p5EQp1de13acVhaz0fbeYC8yI8U7yyExZtbDsc7ifZ22ysE6p2HykutSm+isw/xw1AKegnBU0R6j2Q9TaLq7tAHkT1PlioXGjKhSiqz7TDTLrd2nfZ0ySZ6leUVvOPeFEByXpCw/FR/6RPvvu1Q9Ud5SDvUnunZCc7lSlDEjkMchMEMh4SFi81TIlExzSecPkgHPWGq/kqW+w838=; bm_sz=69428C7AE17E071E4B2DCE0EB16C701B~YAAQTkwQAnZxlV13AQAA8budXgr3MZ+MnJ7Dy3nAhgGeSnjv5Q8kvJNLIeNRMV3nboXDKyvsd5uKoBDv/PJDFfZae1WCUxw9CEOjVTLOS2txNy0oAix/ApoiE+bk2uxhcXaKyXF7kxX8g76i5fHvBVPoFKKJpMn2c/hx2UmrJpVQ0LaucA6G5K4eVWh3zr2622q8Zw==; websitefrescoymas1#lang=en; _gid=GA1.2.602386778.1612200171; RT="z=1&dm=frescoymas.com&si=rsqq6axgei&ss=kkmucpuu&sl=0&tt=0"; bm_sv=3743E1267C2D356578386B3F14002377~JbkxeNpfx511AylmBIHd350UZE3IFmqvTGT8nd3GgVAdzILBqYqY3sSkH2f9p9yOLPv2Cgwo4FB+N4LBmNI3jCB8oQPOFktW5x1mn4CzoaIQgMOb/HNSLKjY8nO1TBV/n3hzu9YnQ3YYXzgh/PUQ/w9yDfUYusw/wCqazuoItMU=; _gat_UA-88296063-3=1',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    url = "https://www.frescoymas.com/V2/storelocator/getStores?search=miami,fl&strDefaultMiles=250&filter="
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    for loc in loclist:
        title = "Fresco y Más en" + " " + loc["Address"]["AddressLine1"]
        store = loc["StoreCode"]
        lat = loc["Address"]["Latitude"]
        longt = loc["Address"]["Longitude"]
        phone = loc["Phone"]
        street = loc["Address"]["AddressLine2"]
        city = loc["Address"]["City"]
        state = loc["Address"]["State"]
        pcode = loc["Address"]["Zipcode"]
        ccode = loc["Address"]["Country"]
        hours = loc["WorkingHours"]
        link = (
            "https://www.frescoymas.com/storedetails?search="
            + str(store)
            + "&zipcode="
            + str(pcode)
            + "&referby=_sd"
        )
        data.append(
            [
                "https://www.frescoymas.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()
