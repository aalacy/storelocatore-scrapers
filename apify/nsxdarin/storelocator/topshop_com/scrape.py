import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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


def fetch_data():
    calocs = [
        "Abbotsford|7 OAKS SHOPPING CENTRE, 32900 SOUTH FRASER WAY|ABBOTSFORD|BC",
        "Anjou|7895 Boulevard Les Galeries D'anjou|Anjou|QC",
        "Banff|125 BANFF AVENUE|Banff|AB",
        "Barrie|465 BAYFIELD STREET|Barrie|ON",
        "Bayshore|100 BAYSHORE DR.|Bayshore|ON",
        "Bloor St|2 BLOOR ST EAST|TORONTO|ON",
        "Boulevard|4150 RUE JEAN-TALON E|MONTREAL|QC",
        "Bramalea|1680 Richmond Street|London|ON",
        "Brossard|2151 BOUL. LAPINIERE|Brossard|QC",
        "Burlington Mall|777 GUELPH LINE|Burlington|ON",
        "Cambridge|355 HESPELER ROAD 355 HESPELER ROAD|Cambridge|ON",
        "Capitale|5401 BOUL. DES GALERIES|Quebec City|QC",
        "Carrefour Laval|3045 Boulevard Le Carrefour|Laval|QC",
        "Centrepoint|6500 YONGE STREET|Willowdale|ON",
        "Chinook|6455 Macleod Trail S.w|Calgary|AB",
        "Coquitlam|100 2929 BARNET HIGHWAY|Coquitlam|BC",
        "Darmouth|21 MICMAC BLVD.|Dartmouth|NS",
        "Dorval|1100 BOUL. MALONEY O.|Gatineau|QC",
        "Edmonton Centre|1200-10250 102 AVENUE NW|Edmonton|AB",
        "Eglinton|1 EGLINTON SQUARE|Toronto|ON",
        "Erin Mills|5100 ERIN MILLS PARKWAY|Mississauga|ON",
        "Fairview|1800 SHEPPARD AVE. EAST|Willowdale|ON",
        "Gatineaul|1100 BOUL. MALONEY O.|Gatineau|QC",
        "Guildford|1400 GUILDFORD TOWN CENTRE|Surrey|BC",
        "Kamloops|674 GRANVILLE STREET|Vancouver|BC",
        "Kingston Cataraqi Centre|945 Gardiners Road|Kingston|QC",
        "Kingsway|109TH ST PRINCESS ELIZ AVE|Edmonton|AB",
        "Kitchener|3050 KINGSWAY DRIVE|Kitchener|ON",
        "Langley|#320 - 19705 FRASER HWY|Langley|BC",
        "Lasalle|7091 BOUL NEWMAN|Lasalle|ON",
        "Laurier|2740 BOUL. LAURIER|Saint Foy|QC",
        "Laval|1600 BOUL. LE CORBUSIER DORVAL|Laval|QC",
        "Lethbridge|200 4TH AVENUE SOUTH|Lethbridge|AB",
        "Limeridge|999 UPPER WENTWORTH ST.|Hamilton|ON",
        "London White Oaks|1105 WELLINGTON RD. SOUTH|London|ON",
        "Londonderry|LONDONDERRY MALL N.W.|Edmonton|AB",
        "Lougheed|9855 AUSTIN ROAD|Burnaby|BC",
        "Mapleview The Bay|900 Maple Avenue|Burlington|ON",
        "Market Mall The Bay|3625 Shaganappi Trail Nw|Calgary|AB",
        "Markville|5000 HWY 7|Markham|ON",
        "Masonville|1680 Richmond Street|London|ON",
        "Mayfair|#221 - 3125 DOUGLAS STREET|Victoria|BC",
        "Medicine Hat|3292 DUNMORE ROAD SE|Medicine Hat|AB",
        "Metrotown Centre The Bay|4850 Kingsway|Burnaby|BC",
        "Midtown Plaza The Bay|201 First Avenue South|Saskatoon|SK",
        "Montreal Temp|Montreal Dtn 585|Montreal|QC",
        "Nanaimo|6631 ISLAND HWY.|Nanaimo|BC",
        "Oakridge|650 41ST AVENUE|Vancouver|BC",
        "Oakville Place|240 Leighland Ave|Oakville|ON",
        "Orchard Park The Bay|1415-2271 Harvey Ave.|Kelowna|BC",
        "Orleans|110 PLACE D'ORLEANS DRIVE|Orleans|ON",
        "Oshawa|419 KING STREET W|Oshawa|ON",
        "Park Royal|725 PARK ROYAL NORTH W|Vancouver|BC",
        "Pen Centre|221 GLENDALE AVENUE|St. Catherines|ON",
        "Penticton|2111 MAIN STREET|Penticton|BC",
        "Pickering|1355 KINGSTON ROAD|Pickering|ON",
        "Pointe Claire Temp|6790 Route Transcanada|Pointe-Claire|QC",
        "Polo Park|1485 Portage Avenue|Winnipeg|AB",
        "Prince George|140- 1600 15TH AVENUE|Prince George|BC",
        "Queen Street|176 Yonge Street|Toronto|ON",
        "Red Deer|4900 MOLLY BANNISTER DR.|Red Deer|AB",
        "Regina|2150 -11TH AVENUE|Regina|SK",
        "Richmond Hill|9350 YONGE STREET|Richmand Hill|ON",
        "Rideau|73 Rideau St|Ottawa|ON",
        "Rockland|2435 ROCKLAND ROAD TMR|Montreal|QC",
        "Rosemere|401 BOUL. LABELLE|Rosemere|QC",
        "Saskatoon|201 FIRST AVENUE SOUTH|Saskatoon|SK",
        "Scarborough Toronto|300 Borough Drive|Scarborough|ON",
        "Sherbrooke|3000 BOUL. DE PORTLAND|Sherbrooke|QC",
        "Sherway|25 The West Mall|Etobicoke|ON",
        "South Centre Calgary|100 Anderson Road Se South Centre Mall|Calgary|AB",
        "Southgate Centre The Bay|150-5015 111th Street|Edmonton|AB",
        "Square One|Square One 100 City Centre Drive|Mississauga|ON",
        "St Bruno|800 BOUL DES PROMENADES|St. Bruno|QC",
        "St. Albert|375 ST. ALBERT TRAIL|St. Albert|AB",
        "St.Laurent|1200 ST. LAUREN BOUL|Ottawa|ON",
        "St.Vital|1225 ST. MARY'S ROAD|Winnipeg|MB",
        "Sunridge|2525 36 STREET NE|Calgary|AB",
        "Sydney|800 GRAND LAKE ROAD|Sydney|NS",
        "Temp Calagary Dtn|200-8th Avenue S.w.|Calgary|AB",
        "The Bay Website|100 Metropolitan Rd|Scarborough|ON",
        "Upper Canada Mall Newmarket|17600 Yonge St. N.|Newmarket|ON",
        "Vancouver|674 Granville Street|Vancouver|BC",
        "Vernon|STE 104900  27TH STREET VERNON|Vernon|BC",
        "Victoria|1150 DOUGLAS STREET|Victoria|BC",
        "Waterloo|550 KING STREET NORTH|Waterloo|ON",
        "West Edmonton Temp|8882 170 St Nw|Edmonton|AB",
        "Windsor|3030 HOWARD AVENUE|Windsor|ON",
        "Winnipeg Dtn|450 PORTAGE AVE.|Winnipeg|MB",
        "Woodbine|500 REXDALE BLVD|Toronto|ON",
        "Yorkdale|3401 Dufferin Street|North York|ON",
    ]

    urls = [
        "https://www.topshop.com/store-locator?country=United+States",
        "https://www.topshop.com/store-locator?country=Canada",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"stores":[' in line:
                items = (
                    line.split('"stores":[')[1]
                    .split('],"selectedStore":{}')[0]
                    .split('"storeId":"')
                )
                for item in items:
                    if "brandPrimaryEStoreId" in item:
                        store = item.split('"')[0]
                        typ = item.split('"brandName":"')[1].split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        website = "topshop.com"
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        add = item.split('"line2":"')[1].split('"')[0]
                        if "Nordstrom" in item:
                            typ = "Nordstrom Topshop"
                        if add == "":
                            add = item.split('"line1":"')[1].split('"')[0]
                        country = "US"
                        city = item.split('"city":"')[1].split('"')[0]
                        if "Canada" in url:
                            country = "CA"
                        state = "<MISSING>"
                        zc = item.split('"postcode":"')[1].split('"')[0]
                        hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item.split('"sunday":"')[1].split('"')[0]
                        )
                        if "-" not in hours:
                            hours = "<MISSING>"
                        loc = "<MISSING>"
                        phone = item.split('"telephoneNumber":"')[1].split('"')[0]
                        if phone == "":
                            phone = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        if "299 CENTRAL" in add:
                            name = "CENTRAL STATES DC"
                            add = "5050 CHAVELLE DRIVE"
                            city = "Washington"
                            state = "DC"
                        if "Cedar Rapids" in name:
                            city = "Cedar Rapids"
                        if country == "CA":
                            for lname in calocs:
                                if name == lname.split("|")[0]:
                                    add = lname.split("|")[1]
                                    city = lname.split("|")[2]
                                    state = lname.split("|")[3]
                                    if "," in add:
                                        add = add.split(",", 1)[1].strip()
                                    zc = "<MISSING>"
                        yield [
                            website,
                            loc,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
