#!/usr/bin/python


class MutualFund:

    '''
    This class wraps all the necessary information contained in Mutual Fund
    '''

    def __init__(self):
        self.fund_id = ""
        self.fund_name = ""

        self.fund_size = 0
        self.mer = 0  # management_expense_ratio
        self.status = "open"
        self.min_inve_initial = 0
        self.min_inve_addition = 0
        self.category = ""
        self.inve_style = ""
        self.inve_objective_strategy = ""

        # Overall performance
        self.growth_of_ten_thousand_YTD = 0
        self.growth_of_ten_thousand_1month = 0
        self.growth_of_ten_thousand_1year = 0
        self.growth_of_ten_thousand_3year = 0
        self.growth_of_ten_thousand_5year = 0
        self.growth_of_ten_thousand_10year = 0

        self.growth_fund_YTD = 0
        self.growth_fund_1month = 0
        self.growth_fund_1year = 0
        self.growth_fund_3year = 0
        self.growth_fund_5year = 0
        self.growth_fund_10year = 0

        self.growth_comp_index_YTD = 0
        self.growth_comp_index_1month = 0
        self.growth_comp_index_1year = 0
        self.growth_comp_index_3year = 0
        self.growth_comp_index_5year = 0
        self.growth_comp_index_10year = 0

        self.growth_comp_category_YTD = 0
        self.growth_comp_category_1month = 0
        self.growth_comp_category_1year = 0
        self.growth_comp_category_3year = 0
        self.growth_comp_category_5year = 0
        self.growth_comp_category_10year = 0

        # Annual performance
        self.annual_perf = {}
        # Key: year;
        # Value: dict {"fund_growth": "", "category_growth": "", "income": "", "net_asset": "",  }
