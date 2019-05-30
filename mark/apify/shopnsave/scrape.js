const Apify = require('apify');
const rp = require('request-promise-native');
const { xml2json, parseData } = require('./tools');

const storeurl =
  'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores';

Apify.main(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: storeurl }],
  });
  await requestList.initialize();

  const crawler = new Apify.BasicCrawler({
    requestList,
    handleRequestFunction: async ({ request }) => {
      const html = await rp(request.url);
      const json = await xml2json(html);

      // The data is nested so define data to this new object
      const data = json.ArrayOfStore.Store;

      for await (const obj of data) {
        await Apify.pushData(parseData(obj));
      }
    },
  });

  await crawler.run();
});
