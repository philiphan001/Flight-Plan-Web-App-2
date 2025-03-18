"""Tax calculator module for financial planning"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class TaxBracket:
    """Represents a tax bracket with rate and income threshold"""
    rate: float
    threshold: float

class TaxCalculator:
    """Handles various tax calculations including federal, state, and payroll taxes"""
    
    # 2024 Federal Tax Brackets
    FEDERAL_SINGLE = [
        TaxBracket(0.10, 11600),
        TaxBracket(0.12, 47150),
        TaxBracket(0.22, 100525),
        TaxBracket(0.24, 191950),
        TaxBracket(0.32, 243725),
        TaxBracket(0.35, 609350),
        TaxBracket(0.37, float('inf'))
    ]

    FEDERAL_MARRIED = [
        TaxBracket(0.10, 23200),
        TaxBracket(0.12, 94300),
        TaxBracket(0.22, 201050),
        TaxBracket(0.24, 383900),
        TaxBracket(0.32, 487450),
        TaxBracket(0.35, 731200),
        TaxBracket(0.37, float('inf'))
    ]

    # FICA Tax Rates for 2024
    SOCIAL_SECURITY_RATE = 0.062
    SOCIAL_SECURITY_WAGE_BASE = 168600
    MEDICARE_RATE = 0.0145
    ADDITIONAL_MEDICARE_RATE = 0.009  # Additional Medicare tax over threshold
    ADDITIONAL_MEDICARE_THRESHOLD_SINGLE = 200000
    ADDITIONAL_MEDICARE_THRESHOLD_MARRIED = 250000

    # State tax rates (2024) - Example structure
    STATE_TAX_RATES = {
        'CA': [
            TaxBracket(0.01, 10099),
            TaxBracket(0.02, 23942),
            TaxBracket(0.04, 37788),
            TaxBracket(0.06, 52455),
            TaxBracket(0.08, 66295),
            TaxBracket(0.093, 338639),
            TaxBracket(0.103, 406364),
            TaxBracket(0.113, 677275),
            TaxBracket(0.123, float('inf'))
        ],
        'NY': [
            TaxBracket(0.04, 8500),
            TaxBracket(0.045, 11700),
            TaxBracket(0.0525, 13900),
            TaxBracket(0.059, 80650),
            TaxBracket(0.0597, 215400),
            TaxBracket(0.0633, 1077550),
            TaxBracket(0.0685, float('inf'))
        ],
        # Add more states as needed
    }

    @staticmethod
    def _calculate_bracketed_tax(income: float, brackets: List[TaxBracket]) -> float:
        """Calculate tax using progressive brackets"""
        if income <= 0:
            return 0

        total_tax = 0
        prev_threshold = 0

        for bracket in brackets:
            if income > prev_threshold:
                taxable_in_bracket = min(income - prev_threshold, bracket.threshold - prev_threshold)
                total_tax += taxable_in_bracket * bracket.rate
                prev_threshold = bracket.threshold
                
                if income <= bracket.threshold:
                    break

        return total_tax

    def calculate_fica_tax(self, income: float, filing_status: str = 'single') -> Dict[str, float]:
        """Calculate FICA (Social Security and Medicare) taxes"""
        # Social Security tax
        ss_tax = min(income * self.SOCIAL_SECURITY_RATE, 
                    self.SOCIAL_SECURITY_WAGE_BASE * self.SOCIAL_SECURITY_RATE)
        
        # Basic Medicare tax
        medicare_tax = income * self.MEDICARE_RATE
        
        # Additional Medicare tax
        threshold = (self.ADDITIONAL_MEDICARE_THRESHOLD_MARRIED 
                    if filing_status == 'married' 
                    else self.ADDITIONAL_MEDICARE_THRESHOLD_SINGLE)
        
        additional_medicare = max(0, 
                                (income - threshold) * self.ADDITIONAL_MEDICARE_RATE 
                                if income > threshold else 0)
        
        total_medicare = medicare_tax + additional_medicare
        
        return {
            'social_security': ss_tax,
            'medicare': total_medicare,
            'total': ss_tax + total_medicare
        }

    def calculate_federal_tax(self, income: float, filing_status: str = 'single') -> float:
        """Calculate federal income tax"""
        brackets = self.FEDERAL_MARRIED if filing_status == 'married' else self.FEDERAL_SINGLE
        return self._calculate_bracketed_tax(income, brackets)

    def calculate_state_tax(self, income: float, state: str) -> float:
        """Calculate state income tax"""
        if state not in self.STATE_TAX_RATES:
            return 0  # Return 0 for states with no income tax or not in our database
        
        return self._calculate_bracketed_tax(income, self.STATE_TAX_RATES[state])

    def calculate_total_tax(self, 
                          income: float, 
                          state: str, 
                          filing_status: str = 'single',
                          spouse_income: float = 0) -> Dict[str, float]:
        """Calculate total taxes including federal, state, and FICA"""
        total_income = income + spouse_income if filing_status == 'married' else income
        
        # Calculate each tax component
        federal_tax = self.calculate_federal_tax(total_income, filing_status)
        state_tax = self.calculate_state_tax(total_income, state)
        
        # Calculate FICA for each income separately
        primary_fica = self.calculate_fica_tax(income, filing_status)
        spouse_fica = (self.calculate_fica_tax(spouse_income, filing_status) 
                      if spouse_income > 0 else {'total': 0})
        
        total_fica = primary_fica['total'] + spouse_fica['total']
        
        # Calculate effective tax rates
        total_tax = federal_tax + state_tax + total_fica
        effective_rate = (total_tax / total_income) if total_income > 0 else 0
        
        return {
            'federal_tax': federal_tax,
            'state_tax': state_tax,
            'fica_tax': total_fica,
            'total_tax': total_tax,
            'effective_tax_rate': effective_rate,
            'net_income': total_income - total_tax
        }

    def get_state_from_city(self, city: str) -> Optional[str]:
        """Map city to state code for tax purposes"""
        # This is a simplified mapping - in a real application, 
        # you would want a more comprehensive database
        city_to_state = {
            'New York': 'NY',
            'Los Angeles': 'CA',
            'San Francisco': 'CA',
            'Chicago': 'IL',
            'Houston': 'TX',
            'Boston': 'MA'
            # Add more cities as needed
        }
        return city_to_state.get(city)
