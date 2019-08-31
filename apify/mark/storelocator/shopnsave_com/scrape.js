const Apify = require('apify');
const rp = require('request-promise-native');
const {
  xml2json,
  formatPhoneNumber,
  validateHours,
} = require('./tools');
const { Poi } = require('./Poi');

const storeurl = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores';

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
        const poiData = {
          locator_domain: 'shopnsavefood.com__api',
          location_name: obj.Name,
          street_address: obj.Address1,
          city: obj.City,
          state: obj.State,
          zip: obj.Zip,
          store_number: obj.StoreID,
          // Although redundant is required due to format Phone Number
          ...((obj.Phone === undefined) && { phone: undefined }),
          ...((obj.Phone !== undefined) && { phone: formatPhoneNumber(obj.Phone) }),
          ...((obj.IsGasStation === 'true') && { location_type: 'Gas Station' }),
          ...((obj.IsGasStation === 'false') && { location_type: 'Store' }),
          latitude: obj.Latitude,
          longitude: obj.Longitude,
          hours_of_operation: validateHours(obj.Hours, obj.Hours2),
        };
        const poi = new Poi(poiData);
        await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
