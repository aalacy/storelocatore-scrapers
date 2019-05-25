const Apify = require('apify');
const { parseString } = require('xml2js');
const rp = require('request-promise-native');

// ENV URL: https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores
const storeurl = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores';
const noDataLabel = 'NO-DATA';

// Converts XML to JSON
const xml2json = xmlString => new Promise((fullfill, reject) => {
  parseString(xmlString, { explicitArray: false }, (err, result) => {
    if (err) {
      reject(err);
    } else {
      fullfill(result);
    }
  });
});

// Makes the a phone number 10 digits with no punctutations
const formatPhoneNumber = string => string.replace(/\D/g, '');

const validateHours = (string1, string2) => {
  if (string1 === 'NO-DATA' || string1.length === 0) {
    return 'NO-DATA';
  }
  if (string1 !== 'NO-DATA' || string1.length !== 0) {
    if (string2 === 'NO-DATA' || string2.length === 0) {
      return string1;
    }
  }
  return `${string1}, ${string2}`;
};

// Simply receives data from the scrape, then formats it.
const parsedShopData = ({
  // If any data points are undefined / null, return 'NO-DATA'
  locatorDomain = 'shopnsavefood.com__api', Name = noDataLabel, Address1 = noDataLabel, City = noDataLabel,
  State = noDataLabel, Zip = noDataLabel, countryCode = 'US', StoreID = noDataLabel,
  Phone: Phone = noDataLabel, IsGasStation = noDataLabel,
  naics = noDataLabel, Latitude = noDataLabel,
  Longitude = noDataLabel, Hours = noDataLabel, Hours2 = noDataLabel,
}) => ({
    // Then set the label similar to the template and make adjustments (gas station / store / hours)
    locator_domain: locatorDomain,
    location_name: Name,
    street_address: Address1,
    city: City,
    state: State,
    zip: Zip,
    country_code: countryCode,
    store_number: StoreID,
    // Although redundant is required due to format Phone Number
    ...((Phone === 'NO-DATA') && { phone: 'NO-DATA' }),
    ...((Phone !== 'NO-DATA') && { phone: formatPhoneNumber(Phone) }),
    ...((IsGasStation === 'true') && { location_type: 'Gas Station' }),
    ...((IsGasStation === 'false') && { location_type: 'Store' }),
    naics_code: naics,
    latitude: Latitude,
    longitude: Longitude,
    hours_of_operation: validateHours(Hours, Hours2),
  });

Apify.main(async () => {
  const requestList = new Apify.RequestList({
    sources: [
      { url: storeurl },
    ],
  });
  await requestList.initialize();

  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({ request }) => {
      const html = await rp(request.url);
      const json = await xml2json(html);

      // The data is nested so define data to this new object
      const data = json.ArrayOfStore.Store;

      /* eslint-disable no-restricted-syntax */
      for await (const obj of data) {
        await Apify.pushData(parsedShopData(obj));
      }
    },
  });

  await crawler.run();
});
