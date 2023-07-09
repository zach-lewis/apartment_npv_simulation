# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 23:35:19 2023

@author: zlewis
"""

from dataclasses import dataclass
from typing import Literal, get_args

BROKER_STRUCTURE = Literal['perc_annual', '1mo_rent', '2mo_rent']

@dataclass
class AptCostSim:
    """Class for Representing Cash Flows / NPV for a 2 Year Apt lease in NYC"""
    
    rent: int
    moving_cost: int
    broker_structure: BROKER_STRUCTURE = 'perc_annual'
    broker_perc: float=.12
    broker_fee: float = 0
    annual_discount: float = .08
    monthly_discount = ((1 + annual_discount) **(1/12)) -1
    second_year_fee: bool=True
    
    def calc_brokers_fee(self):
        options = get_args(BROKER_STRUCTURE)
        assert self.broker_structure in options, f"'{self.broker_structure}' is not in {options}"
        if self.broker_structure == 'perc_annual':
            self.broker_fee = self.broker_perc * (self.rent*12)
        else:
            self.broker_fee = self.rent * int(self.broker_structure[0])

    
    def create_cash_flows(self):
        self.calc_brokers_fee()
        first_month = [self.rent + self.broker_fee + self.moving_cost]
        first_year = first_month + 11*[self.rent]
        
        if self.second_year_fee:
            self.cfs = (first_year + first_year)
        else:
            self.cfs = (first_year + 12*[self.rent])
            
    def npv(self, rate, cfs):
        i = 0
        pv = 0
        
        while i < len(cfs):
            pv += (cfs[i] / (1 + rate) ** i)
            i+= 1        
        return pv * -1
            
    def gen_npv(self):
        self.create_cash_flows()
        return self.npv(self.monthly_discount, self.cfs)
        
def goal_seek(base_apt: AptCostSim,
              comp_apt: AptCostSim,
              lower_bound: float = 1000.00,
              upper_bound: float = 10000.00):
    
    """
    Function to replicate 'goal seek' functionality in Excel. Functionally
    a miniture optimization tool which provides the monthly rent amount necessary
    for a comparison apartment to equal the NPV of the base apartment
    """
    orig_comp_rent = comp_apt.rent
    orig_comp_npv = comp_apt.gen_npv()
    
    current = comp_apt.gen_npv()
    target = base_apt.gen_npv()
    solve = (lower_bound + upper_bound) / 2  
       
    while abs(abs(current) - abs(target)) >= 10:
        if abs(current) > abs(target):
            #Prevents infinite loop when lower_bound == upper_bound
            if lower_bound == solve:
                lower_bound = solve - 10
            upper_bound = solve
        elif abs(current) < abs(target):
            lower_bound = solve

        solve = (lower_bound + upper_bound) / 2
        comp_apt.rent = solve
        current = comp_apt.gen_npv()
    
    print(f'Comparable Apartment Rent for Base Apartment (${base_apt.rent:.0f}): ${comp_apt.rent:.0f}')
    if orig_comp_rent > comp_apt.rent:
        print('Comparison Apartment is potentially overpriced compared to base')
    else:
        print('Comparison Apartment is potentially underpriced compared to base')
    print(f'Difference in NPV: ${target - orig_comp_npv: .2f}')
    return current, comp_apt.rent

if __name__ == '__main__':
    
    apt_622_data = {
        'rent' : 4250,
        'broker_structure' : 'perc_annual',
        'broker_perc' : 0,
        'moving_cost' : 200,
        'second_year_fee' : False
        }
    
    
    comp_apt_data = {
        'rent' : 4000,
        'broker_structure' : '1mo_rent',
        'moving_cost': 1100,
        'second_year_fee': False}
    
    base_apt = AptCostSim(**apt_622_data)
    comp_apt = AptCostSim(**comp_apt_data)
            
    results = goal_seek(base_apt, comp_apt)
  
    
    
    
    




        
    
    