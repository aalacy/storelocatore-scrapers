'use strict';

const   puppeteer   = require('puppeteer'),
        fs          = require('fs-extra'),
        converter   = require('../lib/converter'),
        config      = require('../config.json');

function crawlBot(intialClick, secondaryClick) {

    (async () => {

        try {

            const browser = await puppeteer.launch({ headless: config.headless });
            const context = await browser.createIncognitoBrowserContext();
            const page = await context.newPage();
            const marriottDirectory = 'https://www.marriott.com/hotel-search.mi';
        
            //Setting to mimic a real user of the browser. Google search 'check user agent' to get your own.
            await page.setUserAgent(config.userAgent);

            await page.goto(marriottDirectory);

            //Create .CSV file and prepopulate with columns
            await fs.writeFile('test.csv', 'locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, naics_code, latitude, longitude, hours_of_operation\n');
        
            //Waits for Canada Selector before proceeding to search page
            await page.waitForSelector('.l-accordion');
            await page.click('.tile-directory-result > div:nth-child(5) > h3 > a');
            await page.click('.tile-directory-result > div.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle.open > div > div > a');

            //Enter search page, then wait for pagination last page
            await page.waitForSelector('#results-pagination > div > div.l-display-inline-block > a:nth-child(5)');

            //Get the pagination and use to loop through each page
            const lastPageString = await page.$eval('#results-pagination > div > div.l-display-inline-block > a:nth-child(5)', (div) => { return div.innerText });
            const lastPage = parseInt(lastPageString, 10);

            for (let i = 1; i < lastPage; i++) {

                //Wait for list of properties to appear
                await page.waitForSelector('.property-record-item');

                //Data is split with an outer div and inner div -> start with outer
                const dataPropertyOuter = await page.evaluate(() => 
                    Array.from(document.body.querySelectorAll('.js-property-list-container > div'), 
                        (div) => {
                            return JSON.parse(div.dataset['property'])
                        }
                    )
                );

                //Inner div data
                const dataPropertyInner = await page.evaluate(() =>
                    Array.from(document.body.querySelectorAll('.js-property-list-container > div > div > div > div.js-hotel-location > div > div.m-hotel-address'), 
                        (div) => {
                            return {
                                address: div.dataset['addressLine1'],
                                postalCode: div.dataset['postalCode'],
                                city: div.dataset['city'],
                                state: div.dataset['state'],
                                country: div.dataset['countryDescription'],
                                phoneNumber: div.dataset['contact']
                            }
                        }
                    )
                );

                //Array requires formatting because number has spaces / punctuation and zip code has a space. 
                const formattedDataPropertyInner = converter.formatCanadianArray(dataPropertyInner);

                //Combine outer and inner div objects and return data before moving on
                const dataProperty = converter.combineObjArray(dataPropertyOuter, formattedDataPropertyInner);

                // Loop to insert each row into the .CSV -> Possible to rework in future, if necessary
                for (let obj of dataProperty){
                    let locatorDomain       = 'marriott.com__search__findHotels.mi',
                        locationName        = obj.hotelName,
                        streetAddress       = obj.address,
                        city                = obj.city,
                        state               = obj.state,
                        zip                 = obj.postalCode,
                        countryCode         = obj.country,
                        storeNumber         = 'N/A',
                        phone               = obj.phoneNumber,
                        locationType        = obj.brand,
                        naics               = '',
                        latitude            = obj.lat,
                        longitude           = obj.longitude,
                        hours_of_operation  = ''

                    await fs.appendFile(
                        'test.csv', 
                        `"${locatorDomain}","${locationName}","${streetAddress}","${city}","${state}","${zip}","${countryCode}","${storeNumber}","${phone}","${locationType}","${naics}","${latitude}","${longitude}","${hours_of_operation}"\n`
                    );

                }

                //Sets the delay time to avoid blacklisting from the site. 
                await page.waitFor(config.delayTime);

                //After delay click go to next page
                await page.waitForSelector('#results-pagination > div > div.l-display-inline-block > a.m-pagination-next');
                await page.click(' #results-pagination > div > div.l-display-inline-block > a.m-pagination-next');
            }

            await browser.close(); 

        } catch (error) {

            console.log(error);

        }

    })();

}

module.exports = {
    crawlMarriott
}

            //  Sample dataProperty //

            /*
            returns

            [ ... {   lat: '53.540898',
                longitude: '-113.488115',
                brand: 'CY',
                marshaCode: 'YEGCY',
                hwsInLanguageMissing: 'false',
                blank: '-',
                type: '',
                hotelName: 'Courtyard Edmonton Downtown',
                propertyType: '',
                propMarkerLabel: '',
                propMarkerBedLabel: '',
                index: '',
                address: 'One Thornton Court, 99 Street and Jasper Avenue',
                postalCode: 'T5J2E7',
                city: 'Edmonton',
                state: 'AB',
                country: 'Canada',
                phoneNumber: '17804239999' } ... ]

            */