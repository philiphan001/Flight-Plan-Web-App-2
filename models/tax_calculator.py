"""Tax calculation module for income and payroll taxes"""
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TaxBracket:
    min_income: float
    max_income: float
    rate: float

class TaxCalculator:
    # 2024 Federal Tax Brackets
    SINGLE_BRACKETS = [
        TaxBracket(0, 11600, 0.10),
        TaxBracket(11601, 47150, 0.12),
        TaxBracket(47151, 100525, 0.22),
        TaxBracket(100526, 191950, 0.24),
        TaxBracket(191951, 243725, 0.32),
        TaxBracket(243726, 609350, 0.35),
        TaxBracket(609351, float('inf'), 0.37)
    ]

    # 2024 Federal Tax Brackets - Married Filing Jointly
    JOINT_BRACKETS = [
        TaxBracket(0, 23200, 0.10),
        TaxBracket(23201, 94300, 0.12),
        TaxBracket(94301, 201050, 0.22),
        TaxBracket(201051, 383900, 0.24),
        TaxBracket(383901, 487450, 0.32),
        TaxBracket(487451, 731200, 0.35),
        TaxBracket(731201, float('inf'), 0.37)
    ]

    # State Tax Rates (2024) - Simplified to highest marginal rate for initial implementation
    STATE_TAX_RATES = {
        'AL': 0.05, 'AK': 0.00, 'AZ': 0.0459, 'AR': 0.055, 'CA': 0.133,
        'CO': 0.0444, 'CT': 0.0699, 'DE': 0.066, 'FL': 0.00, 'GA': 0.0575,
        'HI': 0.11, 'ID': 0.058, 'IL': 0.0495, 'IN': 0.0323, 'IA': 0.0600,
        'KS': 0.057, 'KY': 0.045, 'LA': 0.0425, 'ME': 0.0715, 'MD': 0.0575,
        'MA': 0.05, 'MI': 0.0425, 'MN': 0.0985, 'MS': 0.05, 'MO': 0.0495,
        'MT': 0.0675, 'NE': 0.0664, 'NV': 0.00, 'NH': 0.05, 'NJ': 0.1075,
        'NM': 0.059, 'NY': 0.109, 'NC': 0.0499, 'ND': 0.0290, 'OH': 0.0399,
        'OK': 0.0475, 'OR': 0.099, 'PA': 0.0307, 'RI': 0.0599, 'SC': 0.07,
        'SD': 0.00, 'TN': 0.00, 'TX': 0.00, 'UT': 0.0485, 'VT': 0.0875,
        'VA': 0.0575, 'WA': 0.00, 'WV': 0.065, 'WI': 0.0765, 'WY': 0.00
    }

    # FICA rates
    SOCIAL_SECURITY_RATE = 0.062  # 6.2%
    SOCIAL_SECURITY_WAGE_BASE = 168600  # 2024 wage base
    MEDICARE_RATE = 0.0145  # 1.45%
    ADDITIONAL_MEDICARE_RATE = 0.009  # 0.9% additional Medicare tax
    ADDITIONAL_MEDICARE_THRESHOLD_SINGLE = 200000
    ADDITIONAL_MEDICARE_THRESHOLD_JOINT = 250000

    @staticmethod
    def city_to_state(city: str) -> str:
        """Extract state from city string"""
        if ',' in city:
            state = city.split(',')[1].strip().upper()
            return state if len(state) == 2 else None
        return None

    def calculate_federal_tax(self, income: float, is_married: bool = False) -> float:
        """Calculate federal income tax based on filing status"""
        brackets = self.JOINT_BRACKETS if is_married else self.SINGLE_BRACKETS
        tax = 0
        remaining_income = income

        for bracket in brackets:
            if remaining_income <= 0:
                break

            taxable_in_bracket = min(
                remaining_income,
                bracket.max_income - bracket.min_income + 1
            )
            tax += taxable_in_bracket * bracket.rate
            remaining_income -= taxable_in_bracket

        return tax

    def calculate_state_tax(self, income: float, location: str) -> float:
        """Calculate state income tax"""
        state = self.city_to_state(location)
        if not state or state not in self.STATE_TAX_RATES:
            return 0
        return income * self.STATE_TAX_RATES[state]

    def calculate_fica(self, income: float, is_married: bool = False) -> Tuple[float, float]:
        """Calculate FICA taxes (Social Security and Medicare)"""
        # Social Security
        ss_taxable_income = min(income, self.SOCIAL_SECURITY_WAGE_BASE)
        social_security = ss_taxable_income * self.SOCIAL_SECURITY_RATE

        # Medicare
        medicare_threshold = (self.ADDITIONAL_MEDICARE_THRESHOLD_JOINT 
                            if is_married else self.ADDITIONAL_MEDICARE_THRESHOLD_SINGLE)
        
        base_medicare = income * self.MEDICARE_RATE
        additional_medicare = max(0, income - medicare_threshold) * self.ADDITIONAL_MEDICARE_RATE
        medicare = base_medicare + additional_medicare

        return social_security, medicare

    def calculate_total_tax(self, income: float, location: str, is_married: bool = False) -> Dict[str, float]:
        """Calculate total taxes including federal, state, and FICA"""
        federal_tax = self.calculate_federal_tax(income, is_married)
        state_tax = self.calculate_state_tax(income, location)
        social_security, medicare = self.calculate_fica(income, is_married)

        return {
            'federal_tax': federal_tax,
            'state_tax': state_tax,
            'social_security': social_security,
            'medicare': medicare,
            'total_tax': federal_tax + state_tax + social_security + medicare
        }
