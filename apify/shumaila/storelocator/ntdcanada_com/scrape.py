from bs4 import BeautifulSoup
import csv
import re

from sgrequests import SgRequests

session = SgRequests()
headers1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Cookie": "JSESSIONID=22A880E215E990A115B94B507A7EC375; _ga=GA1.2.283289071.1610047025; GSIDjx9ZYpcA7vX1=ce1bb39e-5c8f-422a-b495-5f403b34e599; STSID147343=126c233f-cc07-488e-9010-c0a3e0ce78da; rxVisitor=1611683380951DSC7S3SKJ0KS0J5KHP7U098ODDN78H93; dtSa=-; dtLatC=495; dtPC=6$83380944_986h1vQSMUTRBTCIJAUQECJQCCKNLHUCRHMECH-0e1; rxvt=1611685183171|1611683380955; _gid=GA1.2.1136607805.1611683384; _dc_gtm_UA-157202995-1=1; dtCookie=v_4_srv_6_sn_7BB2C47C0BF4D462EB63BEF4A561E1C4_perc_100000_ol_0_mul_1_app-3A40a3191d61345545_1",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    p = 0
    data = []
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.ntdcanada.com/authorizationserver/oauth/token"
    r = session.post(
        url,
        headers=headers1,
        data={
            "client_id": "atd-ce",
            "client_secret": "secret",
            "grant_type": "client_credentials",
        },
        verify=False,
    ).json()
    auth = "bearer " + r["access_token"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "X-Anonymous-Consents": "%5B%5D",
        "Cookie": "_ga=GA1.2.283289071.1610047025; _gid=GA1.2.1939438744.1610047025; GSIDjx9ZYpcA7vX1=ce1bb39e-5c8f-422a-b495-5f403b34e599; STSID147343=126c233f-cc07-488e-9010-c0a3e0ce78da; rxVisitor=1610105564493145QNJFQVLPVPUBL5DU40UA1U7OV9ESG; dtSa=-; dtCookie=v_4_srv_6_sn_T2NB606K3S5M0NIJUVGS4E0IT6G3A2HM_perc_100000_ol_0_mul_1_app-3A40a3191d61345545_1; dtLatC=18; dtPC=6$306126402_823h1vJKKVDBKDDPNPKQMFLJFWMMFTEHCHKCIM-0e2; _dc_gtm_UA-157202995-1=1; rxvt=1610107927505|1610105564497",
        "Authorization": auth,
    }
    url = "https://www.ntdcanada.com/atdcewebservices/v2/ntd/cms/pages?fields=DEFAULT&pageType=ContentPage&pageLabelOrId=distribution-network&lang=en&curr=CAD"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select("div[class*=body-location]")
    titlelist = []
    for div in divlist:
        title = div.find("h5").text.strip()
        if title in titlelist:
            continue
        titlelist.append(title)
        address = div.find("h6")
        address = re.sub(cleanr, "\n", str(address)).strip().splitlines()
        street = address[0]
        m = 1
        if len(address) > 1:
            while True:
                try:
                    city, state = address[m].split(",", 1)
                    break
                except:
                    m += 1
                    pass
            state, pcode = state.lstrip().split(" ", 1)
            try:
                phone = div.find("a").text
            except:
                phone = div.text.split("Phone", 1)[1].split(":", 1)[1].strip()
        else:
            street = address[0]
            city = "Victoria"
            state = "BC"
            pcode = "V8Z 3B7"
            phone = "(888) 575-0828"
            try:
                street = street.split(city, 1)[0]
            except:
                pass
        store = title.strip().split(" ")[-1]

        data.append(
            [
                "https://www.ntdcanada.com/",
                "https://www.ntdcanada.com/en/distribution-network",
                title,
                street,
                city.replace(",", ""),
                state.replace(",", ""),
                pcode,
                "CA",
                store,
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
