import os
import time
from apiclient import discovery
from google.oauth2 import service_account
import timestamp
import threading
from discord_webhook import DiscordWebhook, DiscordEmbed
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request, jsonify, render_template, redirect
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from colored import fg, bg, attr
from datetime import datetime, time
from twocaptcha import TwoCaptcha
import datetime
from calendar import timegm
import cloudscraper
import webbrowser
import logging
import threading
import traceback
import requests
import random
import string
import shutil
import json
import time
import os
import re
import timestamp
from dicttoxml import dicttoxml
from ebaysdk.utils import getNodeText
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies


# ebay API Credentials

with open('ebay-config.json', 'r') as ebayConfig:
    ebayConfigJson = json.load(ebayConfig)
spreadSheetID = ebayConfigJson['SpreadSheetID']
rangeName = ebayConfigJson['RangeName']
appID = ebayConfigJson['EbayAppID']
devID = ebayConfigJson['EbayDevID']
certID = ebayConfigJson['EbayCertID']
authID = ebayConfigJson['EbayAuthID']
PaymentProfileName = ebayConfigJson['PaymentProfileName']
PaymentProfileID = ebayConfigJson['PaymentProfileID']
ReturnProfileName = ebayConfigJson['ReturnProfileName']
ReturnProfileID = ebayConfigJson['ReturnProfileID']
ShippingProfileName = ebayConfigJson['ShippingProfileName']
ShippingProfileID = ebayConfigJson['ShippingProfileID']

class getSpreadsheet():
    def __init__(self):
        global spreadSheetID
        global rangeName
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        secret_file = os.path.join(os.getcwd(), 'client_secret.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_ID = spreadSheetID
        range_name = rangeName
        sheet = service.spreadsheets()
        while True == True:
            minNew = None
            countNew = 0
            uniqueSKUS = {}
            result = sheet.values().get(spreadsheetId=spreadsheet_ID,range=range_name).execute()
            values = result.get('values', [])
            if not values:
                timestamp.timeStamp('Spreadsheet Not Found', "../ebay.py/~getSpreadsheet")
            else:
                for index, row in enumerate(values):
                    if len(row) == 3:
                        timestamp.timeStamp('Listing Product %s, %s' % (row[0], row[1]), "../ebay.py/~getSpreadsheet")
                        if row[0].lower() not in uniqueSKUS:
                            uniqueSKUS[row[0].lower()] = [row[1]]
                        else:
                            uniqueSKUS[row[0].lower()].append(row[1])
                        if minNew == None:
                            minNew = index+2 
                        else:
                            pass
                        countNew += 1
                    else:
                        pass
            if minNew != None:
                values = []
                update_range = f'{range_name.split("!")[0]}!D{str(minNew)}:D1000'
                for i in range(countNew):
                    values.append(['TRUE'])
                data = {
                    'values' : values
                }
                sheet.values().update(spreadsheetId = spreadsheet_ID, body = data, range = update_range, valueInputOption = 'USER_ENTERED').execute()
            timestamp.timeStamp('Listing Queue Empty', '../ebay.py/~getSpreadsheet')
            if len(uniqueSKUS) > 0:
                for sku in uniqueSKUS:
                    t1 = threading.Thread(target = getStockx, args = [sku, uniqueSKUS[sku]])
                    t1.start()
            time.sleep(60)

class getStockx():
    def __init__(self, sku, inventorySizes):
        self.sku = sku
        self.inventorySizes = inventorySizes 
        global appID
        global devID
        global certID
        global authID
        timestamp.timeStamp(f'Getting StockX Details - {self.sku}', '../ebay.py/~getStockx')
        self.findLink()
    
    def findLink(self):
        headers = {
            'authority': 'stockx.com',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'appos': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'appversion': '0.1',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://stockx.com/search?s=ambush%20dunk',
            'accept-language': 'en-US,en;q=0.9',
        }

        resp = requests.get(
            f'https://stockx.com/api/browse?&_search={self.sku.replace(" ", "%20")}&dataType=product', headers=headers)
        respJson = resp.json()
        try:
            slug = respJson['Products'][0]['urlKey']
            link = f'https://www.stockx.com/{slug}'
            if link != '':
                self.link = link
                self.getProdPage()
        except:
            pass

    def getProdPage(self):
        self.priceList = {}
        headers = {
            'authority': 'stockx.com',
            'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            'appos': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'appversion': '0.1',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://stockx.com/search?s=ambush%20dunk',
            'accept-language': 'en-US,en;q=0.9',
        }

        resp = requests.get(self.link, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        try:
            scripts = soup.find_all('script')
            for script in scripts:
                if 'window.preLoaded = {' in str(script):
                    scriptFormatted = (str(script.contents[0]).replace(
                        'window.preLoaded = ', '').strip())
                    scriptFormatted2 = json.loads(scriptFormatted[:-1])
                    self.prodTitle = scriptFormatted2['product']['shortDescription'].replace('-', ' ').title()
                    self.image = scriptFormatted2['product']['media']['imageUrl']
                    children = scriptFormatted2['product']['children']
                    for child in children:
                        sizeTitle = children[child]['shoeSize'].replace('Y', '').replace('W', '')
                        lowAsk = children[child]['market']['lowestAsk']
                        ebayPrice = int(lowAsk*.9)
                        self.priceList[sizeTitle] = ebayPrice
            self.spawnListings()
        except:
            timestamp.timeStamp(f'Unable to parse all needed elements error', '../ebay.py/~getStockx~getProdPage')
            

    def spawnListings(self):
        for size in self.inventorySizes:
            data = {'Size' : size, 'ListingPrice' : self.priceList[size], 'imageURL' : self.image, 'prodTitle' : self.prodTitle, 'sku' : self.sku}
            t1 = threading.Thread(target=listing, args = [data, appID, devID, certID, authID])
            t1.start()

class listing():
    def __init__(self, stockxData, appID, devID, certID, authID):
        global PaymentProfileName
        global PaymentProfileID
        global ReturnProfileName
        global ReturnProfileID
        global ShippingProfileName
        global ShippingProfileID
        self.listingSize = stockxData['Size']
        self.ListingPrice = stockxData['ListingPrice']
        self.ListingImage = stockxData['imageURL']
        self.ListingProdTitle = stockxData['prodTitle']
        self.ListingSKU = stockxData['sku']
        if self.ListingProdTitle.split(' ')[0] == 'New' and self.ListingProdTitle.split(' ')[1] == 'Balance':
            self.brand = 'New Balance'
        elif self.ListingProdTitle.split(' ')[0] == 'Air' and self.ListingProdTitle.split(' ')[1] == 'Jordan':
            self.brand = 'Jordan'
        else:
            self.brand = self.ListingProdTitle.split(' ')[0]
        
        self.fullListingTitle = f'Brand New DS {self.ListingProdTitle} Size {self.listingSize} {self.ListingSKU}'
        if 'mcdonalds' in self.fullListingTitle.lower():
            self.fullListingTitle = self.fullListingTitle.lower().replace(' mcdonalds', '').title()           
        if len(self.fullListingTitle) > 80:
            self.fullListingTitle = self.fullListingTitle.replace('Brand New ', '')
        if len(self.fullListingTitle) > 80:
            self.fullListingTitle = 'Overflow Dummy Title'
            timestamp.timeStamp('Title Overflow Error, Requires Manual Adjustment', '../ebay.py/~listing')
        timestamp.timeStamp('Preparing to List Item', '../ebay.py/~listing')

        ebaycreds = {'eBayAuthToken':authID}

        ebaycategories = {
            'Mens Sneakers':15709,
            'Womens Sneakers':95672,
            'Unisex Kids Shoes':155202,
            'Mens Hoodies Sweatshirts':155183,
            'Mens Activewear Pants':260956,
        }
        ebayconditions = {
            'New':1000,
            'New other':1500,
            'New w defects':1750,
            'Used':3000,
        }

        NSreplace = 'xmlns="urn:ebay:apis:eBLBaseComponents"'
        shippingservicereplace = '<ShippingServiceCost currencyID="USD">'

        getcategoryspecifics = {

            'CategorySpecific':{
            'CategoryID':ebaycategories['Mens Sneakers'],
            },
            'MaxValuesPerName':1,
            'RequesterCredentials':ebaycreds,
        }

        call = 'GetCategorySpecificsRequest'
        categoryspecificsxml = dicttoxml(getcategoryspecifics, attr_type=False, custom_root=call).decode().replace('<{0}>'.format(call),'<{0} {1}>'.format(call, NSreplace))

        singleshoe = {
            'ErrorLanguage':'en_US',
            'WarningLevel':'High',
            'RequesterCredentials':ebaycreds,
            'Item':{
                'Country':'US',
                'Currency':'USD',
                'Title': self.fullListingTitle,
                'StartPrice':f'{self.ListingPrice}.00',
                'SKU':f'{self.ListingSKU}-{self.listingSize}',
                'Description':f'Thank you for visiting the MKsoles Store!\nThis listing if for the {self.ListingProdTitle}, offered in size {self.listingSize}. This order  will be fulfilled with USPS priority.\nAll products that we sell are 100% Authentic and verified by ebay professional sneaker authenticators, so you can rest assured in your purchase. We will not make any exceptions to this policy, as the ebay authentication process provides the highest level of safety to both buyers and sellers possible.\nAdditionally please note that any new release products sold on/around release day are offered as pre-orders, which may require 7-10 business days to be fulfilled. We aim to fulfill all in stock items within 2-3 business days.\nFinally, please note that all sales are 100% final. We do not offer returns or refunds. Cancellation requests will be fulfilled at seller discretion, prior to the order being fulfilled.\nFeel free to dm with any questions!',
                'DispatchTimeMax':1,
                'InventoryTrackingMethod':'SKU',
                'ListingDuration':'GTC',
                'ListingType':'FixedPriceItem',
                'Location':'New York, NY',
                'AutoPay':'true',
                'ConditionID':ebayconditions['New'],
                'ItemSpecifics':{
                    'NameValueList1':{
                        'Name':"Brand",
                        'Value':self.brand,
                    },
                    'NameValueList2':{
                        'Name':"US Shoe Size (Men's)",
                        'Value':self.listingSize,
                    },
                    'NameValueList3':{
                        'Name':"Style",
                        'Value':'Sneaker',
                    },
                    'NameValueList4':{
                        'Name':"Color",
                        'Value':'Black',
                    },
                    'NameValueList5':{
                        'Name':"Department",
                        'Value':'Men',
                    },
                    'NameValueList6':{
                        'Name':"Type",
                        'Value':'Athletic',
                    },
                },
                'PrimaryCategory':{
                    'CategoryID':ebaycategories['Mens Sneakers'],
                },
                'PictureDetails':{
                    'PictureURL':self.ListingImage,
                },
                'Quantity':1,
                'SellerProfiles':{
                    'SellerPaymentProfile':{
                        'PaymentProfileName' : PaymentProfileName,
                        'PaymentProfileID' : PaymentProfileID
                    },
                    'SellerReturnProfile':{
                        'ReturnProfileName' : ReturnProfileName,
                        'ReturnProfileID' : ReturnProfileID
                    },
                    'SellerShippingProfile':{
                        'ShippingProfileName': ShippingProfileName,
                        'ShippingProfileID' : ShippingProfileID
                    }
                },
                'ReturnPolicy':{
                    'ReturnsAcceptedOption':'ReturnsNotAccepted',
                },
                'ShippingDetails':{
                    'ShippingType':'Flat',
                    'ShippingServiceOptions':{
                        'ShippingServicePriority':1,
                        'ShippingService':'UPSGround',
                        'ShippingServiceCost':'0.0',
                        'ShippingServiceAdditionalCost':'0.00',
                        'FreeShipping':'true',
                    },
                    'GlobalShipping':'true',
                },
                'Site':'US',
                'SiteId':0,
                
            }
        }

        call = 'AddFixedPriceItemRequest'
        singleshoexml = re.sub(r'NameValueList\d+', 'NameValueList', dicttoxml(singleshoe, attr_type=False, custom_root=call).decode().replace('<{0}>'.format(call),'<{0} {1}>'.format(call, NSreplace)).replace('<ShippingServiceCost>', shippingservicereplace))

        r = requests.post('https://api.ebay.com/ws/api.dll', headers={
            'X-EBAY-API-COMPATIBILITY-LEVEL':'1201',
            'X-EBAY-API-CALL-NAME':call.replace('Request',''),
            'X-EBAY-API-SITEID':'0',
            'Content-Type':'text/xml',
            'Content-Length':str(len(singleshoexml))
            }, data=singleshoexml)
        if r.status_code == 200:
            timestamp.timeStamp('Successfully Created Listing ', "../ebay.py/~listing")
            print(r, r.text)


getSpreadsheet()