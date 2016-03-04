#!/usr/bin/python

from mutualfund import MutualFund
import logger

import urllib2
import urllib
import json
import types
from bs4 import BeautifulSoup
import re
import os
import sys

logger = logger.get_logger(__name__)

class Downloader:

    def __init__(self):

        logger.info("__init_() function entry")
        self.init_url = "http://www2.morningstar.ca/Components/FundTable/Services/DataHandler2.ashx?CobrandId=0&Culture=en-CA&SolrQuery=(%3b(%3bCurrency%3aCAD%3bFundCodes%3a**%2c*%2c*%3b%26%3b)%3bSecurityType%3a(FO+FV)%3b%26%3b)&Records=-1&FundView=Morningstar_Analytics"
        self.mutual_fund_url = "http://quote.morningstar.ca/quicktakes/Fund/f_ca.aspx"
        self.mutual_fund_info_url = "http://quote.morningstar.ca/Quicktakes/AjaxProxy.ashx"
        self.mutual_fund_annal_info_url = "http://quote.morningstar.ca/QuickTakes/fund/actionprocess.ashx"
        self.mutual_fund_id_list_file_name = "mutual_fund_id_list.js"

        self.mutualFundCountPerPage = 50
        self.totalMutualFundCount = 0

        self.mutual_fund_id_list = []
        self.mutual_fund_inst_list = []

    def __get_mutual_fund_page_count(self):

        logger.info("__get_mutual_fund_page_count() function entry")

        # Add post parameters
        query_args = {"page": "1",
                      "rp": str(self.mutualFundCountPerPage),
                      "sortname": "StandardName",
                      "sortorder": "asc",
                      "query": "",
                      "qtype": "StandardName",
                      "myFilter": "",
                      "FundIds": ""}
        encoded_args = urllib.urlencode(query_args)
        request = urllib2.Request(self.init_url,encoded_args)

        # Add headers
        request.add_header("Referer",
                           "http://www2.morningstar.ca/Components/FundTable/FundTable2.aspx?CobrandId=0&Culture=en-CA")
        request.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        request.add_header("X-Requested-With",
                           "XMLHttpRequest")

        logger.debug("Http request: %s" % request.get_full_url())

        # Get http response and decode the json
        response = urllib2.urlopen(request)
        json_data = response.read()
        decoded_json = json.loads(json_data)
        self.totalMutualFundCount = int(decoded_json[u"total"])
        logger.debug("Total mutual fund count is %d" % self.totalMutualFundCount)

        return self.totalMutualFundCount / self.mutualFundCountPerPage

    def __save_mutual_fund_id_list_per_page(self, page_number):

        logger.info("__save_mutual_fund_id_list_per_page() function entry. page_number=%d" % page_number)

        # Add post parameters
        query_args = {"page": str(page_number),
                      "rp": str(self.mutualFundCountPerPage),
                      "sortname": "StandardName",
                      "sortorder": "asc",
                      "query": "",
                      "qtype": "StandardName",
                      "myFilter": "",
                      "FundIds": ""}
        encoded_args = urllib.urlencode(query_args)
        request = urllib2.Request(self.init_url,encoded_args)

        # Add headers
        request.add_header("Referer",
                           "http://www2.morningstar.ca/Components/FundTable/FundTable2.aspx?CobrandId=0&Culture=en-CA")
        request.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        request.add_header("X-Requested-With",
                           "XMLHttpRequest")
        logger.debug("Http request: %s" % request.get_full_url())

        # Get http response and decode the json
        response = urllib2.urlopen(request)
        json_data = response.read()
        decoded_json = json.loads(json_data)

        if type(decoded_json[u"rows"]) == types.ListType:
            for row in decoded_json[u"rows"]:
                mutual_fund_id = row[u"id"]
                self.mutual_fund_id_list.append(mutual_fund_id)
                logger.debug("Save mutual fund id %s" % mutual_fund_id)

    def __write_mutual_fund_id_list_to_file(self):

        file_hdlr = open(self.mutual_fund_id_list_file_name, 'w')
        json.dump(self.mutual_fund_id_list, file_hdlr)
        file_hdlr.close()

    def __save_mutual_fund_info(self, mutual_fund_id):

        logger.info("__save_mutual_fund_info() function entry. {'mutual_fund_id': %s}" % mutual_fund_id)

        # Add GET parameters
        query_args = {"t": mutual_fund_id,
                      "region": "CAN",
                      "culture": "en-CA"}
        request = urllib2.Request(self.mutual_fund_url + "?" + urllib.urlencode(query_args))

        # Add headers
        request.add_header("Referer",
                           "http://www2.morningstar.ca/Components/FundTable/FundTable2.aspx?CobrandId=0&Culture=en-CA")
        request.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        logger.debug("Http request: %s" % request.get_full_url())

        # Get http response and extract the url of mutual fund
        response = urllib2.urlopen(request)
        soup = BeautifulSoup(response.read(), 'html.parser')
        script_list = soup.find_all("script")
        pattern = r"t=[a-zA-Z0-9]+&region=CAN&culture=en-CA&cur=CAD&productCode=CAN"
        for script in script_list:
            match = re.search(pattern, unicode(script.string))
            if match:
                url_get_parameter_str = script.string[match.start():match.end()]

                # Split url GET parameter string
                get_parameter_str_list = url_get_parameter_str.split("&")
                get_parameter_dict = {}
                for get_parameter_str in get_parameter_str_list:
                    get_parameter_pair = get_parameter_str.split("=")
                    get_parameter_dict[get_parameter_pair[0]] = get_parameter_pair[1]

                # Create Mutual Fund Instance
                mutual_fund_inst = MutualFund()
                mutual_fund_inst.fund_id = mutual_fund_id

                # save Mutual Fund Head Portion
                self.__save_mutual_fund_head_portion(mutual_fund_inst, get_parameter_dict)

                # save Mutual Fund Objective and Strategy Portion
                self.__save_mutual_fund_obj_strategy_portion(mutual_fund_inst, get_parameter_dict)

                # save Mutual Fund Performance Portion
                self.__save_mutual_fund_performance_portion(mutual_fund_inst, get_parameter_dict)

                # save Mutual Fund Annual Performance Portion
                self.__save_mutual_fund_annual_performance_portion(mutual_fund_inst, get_parameter_dict)

                # Add mutual fund instance to list
                self.mutual_fund_inst_list.append(mutual_fund_inst)

    def __save_mutual_fund_head_portion(self, mutual_fund_inst, get_parameter_dict):

        logger.info(
            "__save_mutual_fund_head_portion() function entry. {'get_parameter_dict': %s}" % get_parameter_dict)

        # Get mutual fund header portion
        query_args = {"url": "http://quotes.morningstar.com/fund/c-header?",
                              "t": get_parameter_dict["t"],
                              "region": get_parameter_dict["region"],
                              "culture": get_parameter_dict["culture"],
                              "cur": get_parameter_dict["cur"],
                              "productCode": get_parameter_dict["productCode"],
                              "showtitle": "1"}
        request = urllib2.Request(self.mutual_fund_info_url + "?" + urllib.urlencode(query_args))
        request.add_header("User-Agent",
                                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        request.add_header("X-Requested-With",
                                   "XMLHttpRequest")
        logger.debug("Http request: %s" % request.get_full_url())

        response = urllib2.urlopen(request)
        mutual_fund_info_head_soup = BeautifulSoup(response.read(), "html.parser")

        # Save fund name
        fund_name_tag = mutual_fund_info_head_soup.find("h1")
        fund_name_tag_str = unicode(fund_name_tag.string).lstrip().rstrip()
        mutual_fund_inst.fund_name = fund_name_tag_str
        logger.debug("Save fund name %s" % fund_name_tag_str)

        # Save fund size
        try:
            total_assets_tag = mutual_fund_info_head_soup.find("span", vkey="TotalAssets")
            total_assets_tag_str = unicode(total_assets_tag.string).lstrip().rstrip()
            mutual_fund_inst.fund_size = float(total_assets_tag_str[0:total_assets_tag_str.find(' ')])
            logger.debug("Save fund size: %f million" % mutual_fund_inst.fund_size)
        except:
            mutual_fund_inst.fund_size = 0
            logger.error("Error reading fund size of fund %s" % mutual_fund_inst.fund_name)

        # Save MER
        try:
            mer_tag = mutual_fund_info_head_soup.find("span", vkey="ExpenseRatio")
            mer_tag_str = unicode(mer_tag.string).lstrip().rstrip()
            mutual_fund_inst.mer = float(mer_tag_str[0:mer_tag_str.find('%')])
            logger.debug("Save fund MER: %f" % mutual_fund_inst.mer)
        except:
            mutual_fund_inst.mer = 0
            logger.error("Error reading MER of fund %s" % mutual_fund_inst.fund_name)

        # Save Status
        try:
            status_tag = mutual_fund_info_head_soup.find("span", vkey="Status")
            status_tag_str = unicode(status_tag.string).lstrip().rstrip()
            mutual_fund_inst.status = status_tag_str
            logger.debug("Save fund status: %s" % mutual_fund_inst.status)
        except:
            mutual_fund_inst.status = "open"
            logger.error("Error reading Status of fund %s" % mutual_fund_inst.fund_name)

        # Save Min-Investment
        try:
            min_investment_tag = mutual_fund_info_head_soup.find("span", vkey="MinInvestment")
            min_investment_tag_str = unicode(min_investment_tag.string).lstrip().rstrip()
            mutual_fund_inst.min_inve_initial = int(min_investment_tag_str.replace(',',''))
            logger.debug("Save fun minimum investment: %d" % mutual_fund_inst.min_inve_initial)
        except:
            mutual_fund_inst.min_inve_initial = 0
            logger.error("Error reading Min Invest of fund %s" % mutual_fund_inst.fund_name)

        # Save Category
        try:
            category_tag = mutual_fund_info_head_soup.find("span", vkey="MorningstarCategory")
            category_tag_str = unicode(category_tag.string).lstrip().rstrip()
            mutual_fund_inst.category = category_tag_str
            logger.debug("Save fund category: %s" % mutual_fund_inst.category)
        except:
            mutual_fund_inst.category = ""
            logger.error("Error reading Category of fund %s" % mutual_fund_inst.fund_name)

        # Save Invest-Style
        try:
            invest_style_tag = mutual_fund_info_head_soup.find("span", vkey="InvestmentStyle")
            for string in invest_style_tag.strings:
                if len(string.lstrip().rstrip()) != 0:
                    mutual_fund_inst.inve_style = string.lstrip().rstrip()
                    logger.debug("Save fund invest style: %s" % mutual_fund_inst.inve_style)
                    break
        except:
            mutual_fund_inst.inve_style = ""
            logger.error("Error reading Invest Style of fund %s" % mutual_fund_inst.fund_name)


    def __save_mutual_fund_obj_strategy_portion(self, mutual_fund_inst, get_parameter_dict):

        logger.info(
            "__save_mutual_fund_obj_strategy_portion() function entry. {'get_parameter_dict': %s}" % get_parameter_dict)

        # Get mutual fund objective and strategy portion
        query_args = {"url": "http://financials.morningstar.com/fund/investObjAndStrategy.html?",
                              "t": get_parameter_dict["t"],
                              "region": get_parameter_dict["region"],
                              "culture": get_parameter_dict["culture"],
                              "cur": get_parameter_dict["cur"],
                              "productCode": get_parameter_dict["productCode"]}
        request = urllib2.Request(self.mutual_fund_info_url + "?" + urllib.urlencode(query_args))
        request.add_header("User-Agent",
                                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        logger.debug("Http request: %s" % request.get_full_url())

        response = urllib2.urlopen(request)
        mutual_fund_info_obj_strategy_soup = BeautifulSoup(response.read(), "html.parser")

        # Save Objective and Strategy
        try:
            div_tag_list = mutual_fund_info_obj_strategy_soup.find_all("div")
            mutual_fund_inst.inve_objective_strategy = unicode(div_tag_list[1].string).lstrip().rstrip()
            logger.debug("Save fund objective and strategy: %s" % mutual_fund_inst.inve_objective_strategy)
        except:
            mutual_fund_inst.inve_objective_strategy = ""
            logger.error("Error reading Invest Objective Strategy of fund %s" % mutual_fund_inst.fund_name)

    def __save_mutual_fund_performance_portion(self, mutual_fund_inst, get_parameter_dict):

        logger.info(
            "__save_mutual_fund_performance_portion() function entry. {'get_parameter_dict': %s}" % get_parameter_dict)

        # Get mutual fund performance portion
        query_args = {"url": "http://quotes.morningstar.com/fund/c-performance?",
                              "t": get_parameter_dict["t"],
                              "region": get_parameter_dict["region"],
                              "culture": get_parameter_dict["culture"],
                              "cur": get_parameter_dict["cur"],
                              "productCode": get_parameter_dict["productCode"]}
        request = urllib2.Request(self.mutual_fund_info_url + "?" + urllib.urlencode(query_args))
        request.add_header("User-Agent",
                                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        request.add_header("X-Requested-With",
                           "XMLHttpRequest")
        logger.debug("Http request: %s" % request.get_full_url())

        response = urllib2.urlopen(request)
        mutual_fund_info_performance_soup = BeautifulSoup(response.read(), "html.parser")

        # Save Performance
        tr_tag_list = mutual_fund_info_performance_soup.find_all("tr")

        # Save growth_of_ten_thousand_YTD
        try:
            if unicode(tr_tag_list[2].contents[3].string) != u"\u2014":
                growth_of_ten_thousand_YTD = float(unicode(tr_tag_list[2].contents[3].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_YTD = growth_of_ten_thousand_YTD
                logger.debug("Save growth_of_ten_thousand_YTD %f" % mutual_fund_inst.growth_of_ten_thousand_YTD)
        except:
            mutual_fund_inst.growth_of_ten_thousand_YTD = 0
            logger.error("Error reading growth_of_ten_thousand_YTD of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_of_ten_thousand_1month
        try:
            if unicode(tr_tag_list[2].contents[5].string) != u"\u2014":
                growth_of_ten_thousand_1month = float(unicode(tr_tag_list[2].contents[5].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_1month = growth_of_ten_thousand_1month
                logger.debug("Save growth_of_ten_thousand_1month %f" % mutual_fund_inst.growth_of_ten_thousand_1month)
        except:
            mutual_fund_inst.growth_of_ten_thousand_1month = 0
            logger.error("Error reading growth_of_ten_thousand_1month of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_of_ten_thousand_1year
        try:
            if unicode(tr_tag_list[2].contents[7].string) != u"\u2014":
                growth_of_ten_thousand_1year = float(unicode(tr_tag_list[2].contents[7].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_1year = growth_of_ten_thousand_1year
                logger.debug("Save growth_of_ten_thousand_1year %f" % mutual_fund_inst.growth_of_ten_thousand_1year)
        except:
            mutual_fund_inst.growth_of_ten_thousand_1year = 0
            logger.error("Error reading growth_of_ten_thousand_1year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_of_ten_thousand_3year
        try:
            if unicode(tr_tag_list[2].contents[11].string) != u"\u2014":
                growth_of_ten_thousand_3year = float(unicode(tr_tag_list[2].contents[11].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_3year = growth_of_ten_thousand_3year
                logger.debug("Save growth_of_ten_thousand_3year %f" % mutual_fund_inst.growth_of_ten_thousand_3year)
        except:
            mutual_fund_inst.growth_of_ten_thousand_3year = 0
            logger.error("Error reading growth_of_ten_thousand_3year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_of_ten_thousand_5year
        try:
            if unicode(tr_tag_list[2].contents[15].string) != u"\u2014":
                growth_of_ten_thousand_5year = float(unicode(tr_tag_list[2].contents[15].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_5year = growth_of_ten_thousand_5year
                logger.debug("Save growth_of_ten_thousand_5year %f" % mutual_fund_inst.growth_of_ten_thousand_5year)
        except:
            mutual_fund_inst.growth_of_ten_thousand_5year = 0
            logger.error("Error reading growth_of_ten_thousand_5year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_of_ten_thousand_10year
        try:
            if unicode(tr_tag_list[2].contents[19].string) != u"\u2014":
                growth_of_ten_thousand_10year = float(unicode(tr_tag_list[2].contents[19].string).replace(",", ""))
                mutual_fund_inst.growth_of_ten_thousand_10year = growth_of_ten_thousand_10year
                logger.debug("Save growth_of_ten_thousand_10year %f" % mutual_fund_inst.growth_of_ten_thousand_10year)
        except:
            mutual_fund_inst.growth_of_ten_thousand_10year = 0
            logger.error("Error reading growth_of_ten_thousand_10year of fund %s" % mutual_fund_inst.fund_name)

        # Save growth_fund_YTD
        try:
            if unicode(tr_tag_list[3].contents[3].string) != u"\u2014":
                growth_fund_YTD = float(unicode(tr_tag_list[3].contents[3].string).replace(",", ""))
                mutual_fund_inst.growth_fund_YTD = growth_fund_YTD
                logger.debug("Save growth_fund_YTD %f" % mutual_fund_inst.growth_fund_YTD)
        except:
            mutual_fund_inst.growth_fund_YTD = 0
            logger.error("Error reading growth_fund_YTD of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_fund_1month
        try:
            if unicode(tr_tag_list[3].contents[5].string) != u"\u2014":
                growth_fund_1month = float(unicode(tr_tag_list[3].contents[5].string).replace(",", ""))
                mutual_fund_inst.growth_fund_1month = growth_fund_1month
                logger.debug("Save growth_fund_1month %f" % mutual_fund_inst.growth_fund_1month)
        except:
            mutual_fund_inst.growth_fund_1month = 0
            logger.error("Error reading growth_fund_1month of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_fund_1year
        try:
            if unicode(tr_tag_list[3].contents[7].string) != u"\u2014":
                growth_fund_1year = float(unicode(tr_tag_list[3].contents[7].string).replace(",", ""))
                mutual_fund_inst.growth_fund_1year = growth_fund_1year
                logger.debug("Save growth_fund_1year %f" % mutual_fund_inst.growth_fund_1year)
        except:
            mutual_fund_inst.growth_fund_1year = 0
            logger.error("Error reading growth_fund_1year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_fund_3year
        try:
            if unicode(tr_tag_list[3].contents[11].string) != u"\u2014":
                growth_fund_3year = float(unicode(tr_tag_list[3].contents[11].string).replace(",", ""))
                mutual_fund_inst.growth_fund_3year = growth_fund_3year
                logger.debug("Save growth_fund_3year %f" % mutual_fund_inst.growth_fund_3year)
        except:
            mutual_fund_inst.growth_fund_3year = 0
            logger.error("Error reading growth_fund_3year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_fund_5year
        try:
            if unicode(tr_tag_list[3].contents[15].string) != u"\u2014":
                growth_fund_5year = float(unicode(tr_tag_list[3].contents[15].string).replace(",", ""))
                mutual_fund_inst.growth_fund_5year = growth_fund_5year
                logger.debug("Save growth_fund_5year %f" % mutual_fund_inst.growth_fund_5year)
        except:
            mutual_fund_inst.growth_fund_5year = 0
            logger.error("Error reading growth_fund_5year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_fund_10year
        try:
            if unicode(tr_tag_list[3].contents[19].string) != u"\u2014":
                growth_fund_10year = float(unicode(tr_tag_list[3].contents[19].string).replace(",", ""))
                mutual_fund_inst.growth_fund_10year = growth_fund_10year
                logger.debug("Save growth_fund_10year %f" % mutual_fund_inst.growth_fund_10year)
        except:
            mutual_fund_inst.growth_fund_10year = 0
            logger.error("Error reading growth_fund_10year of fund %s" % mutual_fund_inst.fund_name)

        # Save growth_comp_index_YTD
        try:
            if unicode(tr_tag_list[4].contents[3].string) != u"\u2014":
                growth_comp_index_YTD = float(unicode(tr_tag_list[4].contents[3].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_YTD = growth_comp_index_YTD
                logger.debug("Save growth_comp_index_YTD %f" % mutual_fund_inst.growth_comp_index_YTD)
        except:
            mutual_fund_inst.growth_comp_index_YTD = 0
            logger.error("Error reading growth_comp_index_YTD of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_index_1month
        try:
            if unicode(tr_tag_list[4].contents[5].string) != u"\u2014":
                growth_comp_index_1month = float(unicode(tr_tag_list[4].contents[5].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_1month = growth_comp_index_1month
                logger.debug("Save growth_comp_index_1month %f" % mutual_fund_inst.growth_comp_index_1month)
        except:
            mutual_fund_inst.growth_comp_index_1month = 0
            logger.error("Error reading growth_comp_index_1month of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_index_1year
        try:
            if unicode(tr_tag_list[4].contents[7].string) != u"\u2014":
                growth_comp_index_1year = float(unicode(tr_tag_list[4].contents[7].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_1year = growth_comp_index_1year
                logger.debug("Save growth_comp_index_1year %f" % mutual_fund_inst.growth_comp_index_1year)
        except:
            mutual_fund_inst.growth_comp_index_1year = 0
            logger.error("Error reading growth_comp_index_1year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_index_3year
        try:
            if unicode(tr_tag_list[4].contents[11].string) != u"\u2014":
                growth_comp_index_3year = float(unicode(tr_tag_list[4].contents[11].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_3year = growth_comp_index_3year
                logger.debug("Save growth_comp_index_3year %f" % mutual_fund_inst.growth_comp_index_3year)
        except:
            mutual_fund_inst.growth_comp_index_3year = 0
            logger.error("Error reading growth_comp_index_3year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_index_5year
        try:
            if unicode(tr_tag_list[4].contents[15].string) != u"\u2014":
                growth_comp_index_5year = float(unicode(tr_tag_list[4].contents[15].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_5year = growth_comp_index_5year
                logger.debug("Save growth_comp_index_5year %f" % mutual_fund_inst.growth_comp_index_5year)
        except:
            mutual_fund_inst.growth_comp_index_5year = 0
            logger.error("Error reading growth_comp_index_5year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_index_10year
        try:
            if unicode(tr_tag_list[4].contents[19].string) != u"\u2014":
                growth_comp_index_10year = float(unicode(tr_tag_list[4].contents[19].string).replace(",", ""))
                mutual_fund_inst.growth_comp_index_10year = growth_comp_index_10year
                logger.debug("Save growth_comp_index_10year %f" % mutual_fund_inst.growth_comp_index_10year)
        except:
            mutual_fund_inst.growth_comp_index_10year = 0
            logger.error("Error reading growth_comp_index_10year of fund %s" % mutual_fund_inst.fund_name)

        # Save growth_comp_category_YTD
        try:
            if unicode(tr_tag_list[5].contents[3].string) != u"\u2014":
                growth_comp_category_YTD = float(unicode(tr_tag_list[5].contents[3].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_YTD = growth_comp_category_YTD
                logger.debug("Save growth_comp_category_YTD %f" % mutual_fund_inst.growth_comp_category_YTD)
        except:
            mutual_fund_inst.growth_comp_category_YTD = 0
            logger.error("Error reading growth_comp_category_YTD of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_category_1month
        try:
            if unicode(tr_tag_list[5].contents[5].string) != u"\u2014":
                growth_comp_category_1month = float(unicode(tr_tag_list[5].contents[5].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_1month = growth_comp_category_1month
                logger.debug("Save growth_comp_category_1month %f" % mutual_fund_inst.growth_comp_category_1month)
        except:
            mutual_fund_inst.growth_comp_category_1month = 0
            logger.error("Error reading growth_comp_category_1month of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_category_1year
        try:
            if unicode(tr_tag_list[5].contents[7].string) != u"\u2014":
                growth_comp_category_1year = float(unicode(tr_tag_list[5].contents[7].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_1year = growth_comp_category_1year
                logger.debug("Save growth_comp_category_1year %f" % mutual_fund_inst.growth_comp_category_1year)
        except:
            mutual_fund_inst.growth_comp_category_1year = 0
            logger.error("Error reading growth_comp_category_1year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_category_3year
        try:
            if unicode(tr_tag_list[5].contents[11].string) != u"\u2014":
                growth_comp_category_3year = float(unicode(tr_tag_list[5].contents[11].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_3year = growth_comp_category_3year
                logger.debug("Save growth_comp_category_3year %f" % mutual_fund_inst.growth_comp_category_3year)
        except:
            mutual_fund_inst.growth_comp_category_3year = 0
            logger.error("Error reading growth_comp_category_3year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_category_5year
        try:
            if unicode(tr_tag_list[5].contents[15].string) != u"\u2014":
                growth_comp_category_5year = float(unicode(tr_tag_list[5].contents[15].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_5year = growth_comp_category_5year
                logger.debug("Save growth_comp_category_5year %f" % mutual_fund_inst.growth_comp_category_5year)
        except:
            mutual_fund_inst.growth_comp_category_5year = 0
            logger.error("Error reading growth_comp_category_5year of fund %s" % mutual_fund_inst.fund_name)
        # Save growth_comp_category_10year
        try:
            if unicode(tr_tag_list[5].contents[19].string) != u"\u2014":
                growth_comp_category_10year = float(unicode(tr_tag_list[5].contents[19].string).replace(",", ""))
                mutual_fund_inst.growth_comp_category_10year = growth_comp_category_10year
                logger.debug("Save growth_comp_category_10year %f" % mutual_fund_inst.growth_comp_category_10year)
        except:
            mutual_fund_inst.growth_comp_category_10year = 0
            logger.error("Error reading growth_comp_category_10year of fund %s" % mutual_fund_inst.fund_name)

    def __save_mutual_fund_annual_performance_portion(self, mutual_fund_inst, get_parameter_dict):

        logger.info(
            "__save_mutual_fund_annual_performance_portion() function entry. {'get_parameter_dict': %s}" % get_parameter_dict)

        # Get mutual fund performance portion
        query_args = {"lk": "/PerformanceHtml/fund/performance-history.action",
                      "sn": "MSTAR",
                      "t": get_parameter_dict["t"],
                      "s": "",
                      "ndec": "2",
                      "ep": "true",
                      "align": "m",
                      "y": "10",
                      "region": get_parameter_dict["region"],
                      "culture": get_parameter_dict["culture"],
                      "comparisonRemove": "true",
                      "ops": "clear",
                      "cur": get_parameter_dict["cur"]}
        request = urllib2.Request(self.mutual_fund_annal_info_url + "?" + urllib.urlencode(query_args))
        request.add_header("User-Agent",
                           "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36")
        request.add_header("X-Requested-With",
                           "XMLHttpRequest")
        logger.debug("Http request: %s" % request.get_full_url())

        response = urllib2.urlopen(request, timeout=20)
        mutual_fund_info_annual_perf_soup = BeautifulSoup(response.read(), "html.parser")

        # Save Annual Performance
        year_list = []
        year_th_tag_list = mutual_fund_info_annual_perf_soup.find_all("th", class_="col_data divide")
        for year_th_tag in year_th_tag_list:
            year_list.append(int(unicode(year_th_tag.string)))

        tbody_tag = mutual_fund_info_annual_perf_soup.find("tbody")

        tbody_soup = BeautifulSoup(str(tbody_tag), "html.parser")
        tr_tag_list = tbody_soup.find_all("tr")

        # Initialize lists
        fund_perf_list = []
        category_perf_list = []
        income_list = []
        asset_list = []

        # Save fund perf list
        try:
            if tr_tag_list is not None and len(tr_tag_list) > 0:
                fund_tr_soup = BeautifulSoup(str(tr_tag_list[0]), "html.parser")
                td_tag_list = fund_tr_soup.find_all("td")
                for td_tag in td_tag_list:
                    if td_tag.string == u"\u2014" or td_tag.string is None:
                        fund_perf_list.append(0)
                    else:
                        fund_perf_list.append(float(td_tag.string))
            if len(fund_perf_list) != len(year_list)+1:
                for i in range(len(year_list)+1 - len(fund_perf_list)):
                    fund_perf_list.append(0)
        except:
            logger.error("Error parsing fund perf list")
            fund_perf_list = [0] * (len(year_list) + 1)

        # Save category perf list
        try:
            if tr_tag_list is not None and len(tr_tag_list) > 1:
                category_tr_soup = BeautifulSoup(str(tr_tag_list[1]), "html.parser")
                td_tag_list = category_tr_soup.find_all("td")
                for td_tag in td_tag_list:
                    if td_tag.string == u"\u2014" or td_tag.string is None:
                        category_perf_list.append(0)
                    else:
                        category_perf_list.append(float(td_tag.string))
            if len(category_perf_list) != len(year_list)+1:
                for i in range(len(year_list)+1 - len(category_perf_list)):
                    category_perf_list.append(0)
        except:
            logger.error("Error parsing category perf list")
            category_perf_list = [0] * (len(year_list) + 1)

        # Save fund income
        try:
            if tr_tag_list is not None and len(tr_tag_list) > 3:
                income_tr_soup = BeautifulSoup(str(tr_tag_list[3]), "html.parser")
                td_tag_list = income_tr_soup.find_all("td")
                for td_tag in td_tag_list:
                    if td_tag.string == u"\u2014" or td_tag.string is None:
                        income_list.append(0)
                    else:
                        income_list.append(float(td_tag.string))
            if len(income_list) != len(year_list)+1:
                for i in range(len(year_list)+1 - len(income_list)):
                    income_list.append(0)
        except:
            logger.error("Error parsing fund income list")
            income_list = [0] * (len(year_list) + 1)

        # Save fund net assets
        try:
            if tr_tag_list is not None and len(tr_tag_list) > 5:
                asset_tr_soup = BeautifulSoup(str(tr_tag_list[5]), "html.parser")
                td_tag_list = asset_tr_soup.find_all("td")
                for td_tag in td_tag_list:
                    if td_tag.string == u"\u2014" or td_tag.string is None:
                        asset_list.append(0)
                    else:
                        asset_list.append(float(td_tag.string.lstrip().rstrip().replace(",", "")))
            if len(asset_list) != len(year_list)+1:
                for i in range(len(year_list)+1 - len(asset_list)):
                    asset_list.append(0)
        except:
            logger.error("Error parsing fund net asset list")
            asset_list = [0] * (len(year_list) + 1)

        # Save info to Mutual Fund Instance
        for i in range(len(year_list)):
            mutual_fund_inst.annual_perf[year_list[i]] = {"fund_growth": fund_perf_list[i],
                                                          "category_growth": category_perf_list[i],
                                                          "income": income_list[i],
                                                          "net_asset": asset_list[i]}
        logger.debug("Save annual performance: %s" % mutual_fund_inst.annual_perf)


    def save_all_mutual_fund_info(self):

        if os.path.exists(self.mutual_fund_id_list_file_name) and os.path.isfile(self.mutual_fund_id_list_file_name):
            logger.debug("Read mutual fund id list from %s" % self.mutual_fund_id_list_file_name)
            file_hdlr = open(self.mutual_fund_id_list_file_name, 'r')
            self.mutual_fund_id_list = json.load(file_hdlr)
            file_hdlr.close()
        else:
            logger.debug("%s file does not exist, need to read from Internet and write to file" % self.mutual_fund_id_list_file_name)
            page_count = self.__get_mutual_fund_page_count()
            for i in range(page_count):
                if i > 0:
                    self.__save_mutual_fund_id_list_per_page(i)
            self.__write_mutual_fund_id_list_to_file()
        print "Total %d Mutual Fund need to be downloaded." % len(self.mutual_fund_id_list)

        count = 0
        for fund_id in self.mutual_fund_id_list:
            self.__save_mutual_fund_info(fund_id)
            count += 1
            sys.stdout.write("\rNow processing #%d Mutual Fund" % count)
            sys.stdout.flush()
        print "Successfully download %d Mutual Fund" % len(self.mutual_fund_id_list)

if __name__ == '__main__':
    downloader = Downloader()
    downloader._Downloader__save_mutual_fund_info("F00000V7J8")
