const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.doncuco.com/order-online-1';
async function scrape(){

 return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        
     function mainhead(i)

        {
            if(10>i)

                {
        var link = $('#x0ateinlineContent-gridContainer').find('div').find('a').eq(i).attr('href');
        
        
        request(link,(err,res,html)=>{

          if(!err && res.statusCode==200){

            const $  =cheerio.load(html);
            var location_name_tmp = $('h2').find('span').find('span').text().replace('DON CUCO MEXICAN RESTAURANT:DON CUCO MEXICAN RESTAURANT:','');
            var location_name = location_name_tmp.replace('DON CUCO MEXICAN RESTAURANT:','');
             
            var main1 =$('h1').text();
            var address_tmp = main1.split('ADDRESS');
            var hour = address_tmp[0].replace('HOURS','');
            var address_tmp1 =address_tmp[1].split('CONTACTPhone:');
            var phone_tmp = address_tmp1[1].split('\n');
            var phone = phone_tmp[0];
            var address_tmp2 = address_tmp1[0];
            var address_tmp3 = address_tmp2.split('.');
            if(address_tmp3.length == 2){
              var address = address_tmp3[0];
              var state_tmp = address_tmp3[1].replace(/\n/g, '');
              var state_tmp1 = state_tmp.split(',');
              var city = state_tmp1[0];
              var state_tmp2 = state_tmp1[1].split(' ');
              var state = state_tmp2[1];
              var zip = state_tmp2[2];
              
              

            }
            else if(address_tmp3.length == 3){
              var address = address_tmp3[0]+''+address_tmp3[1];
              var state_tmp = address_tmp3[2].split(',');
              var city = state_tmp[0];
              var state_tmp1 = state_tmp[1].split(' ');
              var state = state_tmp1[1];
              var zip = state_tmp1[2];
              


            }
             items.push({  

                locator_domain: 'https://www.doncuco.com/', 

                location_name: location_name, 

                street_address: address,

                city: city, 

                state: state,

                zip:  zip,

                country_code: 'US',

                store_number: '<MISSING>',

                phone: phone,

                location_type: 'doncuco',

                latitude: '<MISSING>',

                longitude: '<MISSING>', 

                hours_of_operation: hour});
                mainhead(i+1);
        
             
          }
        });

     
       
        }


      else{
  
      resolve(items);
  
      }
} 

mainhead(7); 
               

            
            }
    });
  });
}

  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
     // console.log(data);
      await Apify.pushData(data);
    
    });