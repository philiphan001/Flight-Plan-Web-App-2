"""Tax calculation service for payroll and income taxes"""
from typing import Dict, Tuple, List, Union
from decimal import Decimal

class TaxCalculator:
    # 2024 Federal Tax Brackets
    SINGLE_BRACKETS = [
        (11_600, 0.10),
        (47_150, 0.12),
        (100_525, 0.22),
        (191_950, 0.24),
        (243_725, 0.32),
        (609_350, 0.35),
        (float('inf'), 0.37)
    ]

    MARRIED_BRACKETS = [
        (23_200, 0.10),
        (94_300, 0.12),
        (201_050, 0.22),
        (383_900, 0.24),
        (487_450, 0.32),
        (731_200, 0.35),
        (float('inf'), 0.37)
    ]

    # 2024 FICA Limits
    SOCIAL_SECURITY_LIMIT = 168_600
    SOCIAL_SECURITY_RATE = 0.062
    MEDICARE_RATE = 0.0145
    ADDITIONAL_MEDICARE_THRESHOLD = 200_000
    ADDITIONAL_MEDICARE_RATE = 0.009

    @classmethod
    def calculate_fica_taxes(cls, income: float) -> Dict[str, float]:
        """Calculate FICA (Social Security and Medicare) taxes"""
        # Social Security tax (capped at limit)
        ss_taxable_income = min(income, cls.SOCIAL_SECURITY_LIMIT)
        social_security_tax = ss_taxable_income * cls.SOCIAL_SECURITY_RATE

        # Base Medicare tax (no income limit)
        medicare_tax = income * cls.MEDICARE_RATE

        # Additional Medicare tax for high earners
        additional_medicare_tax = max(0, income - cls.ADDITIONAL_MEDICARE_THRESHOLD) * cls.ADDITIONAL_MEDICARE_RATE

        total_medicare = medicare_tax + additional_medicare_tax
        total_fica = social_security_tax + total_medicare

        return {
            'social_security_tax': round(social_security_tax, 2),
            'medicare_tax': round(total_medicare, 2),
            'total_fica': round(total_fica, 2)
        }

    @classmethod
    def calculate_federal_income_tax(cls, income: float, filing_status: str = 'single',
                                   deductions: float = 0) -> Dict[str, float]:
        """Calculate federal income tax based on filing status and income"""
        # Standard deduction for 2024
        standard_deduction = 14_600 if filing_status.lower() == 'single' else 29_200

        # Use the larger of standard deduction or itemized deductions
        total_deductions = max(standard_deduction, deductions)
        taxable_income = max(0, income - total_deductions)

        # Select tax brackets based on filing status
        brackets = cls.SINGLE_BRACKETS if filing_status.lower() == 'single' else cls.MARRIED_BRACKETS

        tax = 0
        previous_bracket = 0
        for bracket, rate in brackets:
            if taxable_income > previous_bracket:
                taxable_in_bracket = min(taxable_income - previous_bracket, bracket - previous_bracket)
                tax += taxable_in_bracket * rate
            previous_bracket = bracket

        return {
            'taxable_income': round(taxable_income, 2),
            'federal_tax': round(tax, 2)
        }

    @classmethod
    def calculate_total_tax_burden(cls, income: float, filing_status: str = 'single',
                                 deductions: float = 0) -> Dict[str, float]:
        """Calculate total tax burden including both FICA and federal income tax"""
        fica_taxes = cls.calculate_fica_taxes(income)
        federal_taxes = cls.calculate_federal_income_tax(income, filing_status, deductions)

        total_tax = fica_taxes['total_fica'] + federal_taxes['federal_tax']
        effective_rate = (total_tax / income) if income > 0 else 0

        return {
            'fica_taxes': fica_taxes,
            'federal_taxes': federal_taxes,
            'total_tax': round(total_tax, 2),
            'effective_tax_rate': round(effective_rate * 100, 2)
        }

    @classmethod
    def calculate_joint_tax_burden(cls, primary_income: float, spouse_income: float,
                                 deductions: float = 0) -> Dict[str, float]:
        """Calculate total tax burden for married couple filing jointly"""
        # Calculate individual FICA taxes (these are always calculated separately)
        primary_fica = cls.calculate_fica_taxes(primary_income)
        spouse_fica = cls.calculate_fica_taxes(spouse_income)

        # Calculate joint federal income tax
        combined_income = primary_income + spouse_income
        federal_taxes = cls.calculate_federal_income_tax(combined_income, 'married', deductions)

        total_fica = primary_fica['total_fica'] + spouse_fica['total_fica']
        total_tax = total_fica + federal_taxes['federal_tax']
        effective_rate = (total_tax / combined_income) if combined_income > 0 else 0

        return {
            'primary_fica': primary_fica,
            'spouse_fica': spouse_fica,
            'federal_taxes': federal_taxes,
            'total_tax': round(total_tax, 2),
            'effective_tax_rate': round(effective_rate * 100, 2)
        }
