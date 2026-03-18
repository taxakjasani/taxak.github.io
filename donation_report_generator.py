#!/usr/bin/env python3
"""
Monthly Donation Report Generator

A Python automation tool that generates professional monthly PDF reports for tracking donations and supporter contributions.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Tuple, Optional

import requests
import matplotlib.pyplot as plt
from fpdf import FPDF


class DonationReportGenerator:
    """
    Main class for generating monthly donation reports
    """
    
    def __init__(self, api_token: str, api_base_url: str = "https://api.donationplatform.com"):
        self.api_token = api_token
        self.api_base_url = api_base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
    def get_donations_for_month(self, year: int, month: int) -> List[Dict]:
        """
        Retrieve all donations for a specific month from the API
        """
        # Calculate start and end dates for the month
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        # Get last day of the month
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).strftime('%Y-%m-%d')
        
        print(f"Fetching donations for {year}-{month:02d} ({start_date} to {end_date})...")
        
        # API endpoint for donations (this is a placeholder - actual endpoint depends on the API)
        url = f"{self.api_base_url}/donations"
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def analyze_donations(self, donations: List[Dict]) -> Dict:
        """
        Analyze donation data to extract key statistics
        """
        if not donations:
            return {
                'total_supporters': 0,
                'unique_supporters': 0,
                'total_donations': 0,
                'total_revenue': 0.0,
                'average_donation': 0.0,
                'top_supporters': [],
                'daily_revenue': {}
            }
        
        # Extract supporter IDs and donation amounts
        supporter_ids = []
        donation_amounts = []
        daily_revenue = {}
        
        for donation in donations:
            supporter_id = donation.get('supporter_id')
            amount = float(donation.get('amount', 0))
            created_at = donation.get('created_at', '')
            
            supporter_ids.append(supporter_id)
            donation_amounts.append(amount)
            
            # Group by date for daily revenue
            if created_at:
                date_str = created_at.split('T')[0]  # Extract date part from ISO format
                if date_str in daily_revenue:
                    daily_revenue[date_str] += amount
                else:
                    daily_revenue[date_str] = amount
        
        # Calculate statistics
        total_supporters = len(supporter_ids)
        unique_supporters = len(set(supporter_ids)) if supporter_ids else 0
        total_donations = len(donations)
        total_revenue = sum(donation_amounts)
        average_donation = total_revenue / total_donations if total_donations > 0 else 0.0
        
        # Get top supporters
        supporter_totals = {}
        for donation in donations:
            supporter_id = donation.get('supporter_id')
            supporter_name = donation.get('supporter_name', f'Supporter {supporter_id}')
            amount = float(donation.get('amount', 0))
            
            if supporter_id in supporter_totals:
                supporter_totals[supporter_id]['total'] += amount
                supporter_totals[supporter_id]['count'] += 1
            else:
                supporter_totals[supporter_id] = {
                    'name': supporter_name,
                    'total': amount,
                    'count': 1
                }
        
        # Sort supporters by total donation amount
        sorted_supporters = sorted(
            supporter_totals.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        top_supporters = [
            {
                'name': supporter_data['name'],
                'total_donated': supporter_data['total'],
                'donation_count': supporter_data['count']
            }
            for _, supporter_data in sorted_supporters[:10]
        ]
        
        return {
            'total_supporters': total_supporters,
            'unique_supporters': unique_supporters,
            'total_donations': total_donations,
            'total_revenue': total_revenue,
            'average_donation': average_donation,
            'top_supporters': top_supporters,
            'daily_revenue': daily_revenue
        }
    
    def create_visualizations(self, analysis_data: Dict, year: int, month: int) -> Tuple[str, str]:
        """
        Create visualization charts and save them as images
        Returns paths to the saved images
        """
        # Create directory for images if it doesn't exist
        img_dir = "report_images"
        os.makedirs(img_dir, exist_ok=True)
        
        # Daily Revenue Chart
        daily_revenue_path = os.path.join(img_dir, f"daily_revenue_{year}_{month}.png")
        if analysis_data['daily_revenue']:
            dates = list(analysis_data['daily_revenue'].keys())
            revenues = list(analysis_data['daily_revenue'].values())
            
            plt.figure(figsize=(12, 6))
            plt.bar(dates, revenues)
            plt.title(f'Daily Revenue - {calendar.month_name[month]} {year}')
            plt.xlabel('Date')
            plt.ylabel('Revenue ($)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(daily_revenue_path)
            plt.close()
        else:
            # Create an empty chart image
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center')
            plt.title(f'Daily Revenue - {calendar.month_name[month]} {year}')
            plt.savefig(daily_revenue_path)
            plt.close()
        
        # Top Supporters Chart
        top_supporters_path = os.path.join(img_dir, f"top_supporters_{year}_{month}.png")
        if analysis_data['top_supporters']:
            names = [s['name'] for s in analysis_data['top_supporters']]
            totals = [s['total_donated'] for s in analysis_data['top_supporters']]
            
            plt.figure(figsize=(12, 8))
            bars = plt.barh(names, totals)
            plt.title(f'Top 10 Supporters - {calendar.month_name[month]} {year}')
            plt.xlabel('Total Donated ($)')
            plt.gca().invert_yaxis()  # Show highest donors at top
            
            # Add value labels on bars
            for bar, total in zip(bars, totals):
                width = bar.get_width()
                plt.text(width, bar.get_y() + bar.get_height()/2, f'${total:.2f}', 
                        ha='left', va='center')
            
            plt.tight_layout()
            plt.savefig(top_supporters_path)
            plt.close()
        else:
            # Create an empty chart image
            plt.figure(figsize=(12, 8))
            plt.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center')
            plt.title(f'Top 10 Supporters - {calendar.month_name[month]} {year}')
            plt.savefig(top_supporters_path)
            plt.close()
        
        return daily_revenue_path, top_supporters_path
    
    def generate_pdf_report(self, analysis_data: Dict, year: int, month: int, 
                           daily_revenue_img: str, top_supporters_img: str) -> str:
        """
        Generate the final PDF report
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Monthly Donation Report - {calendar.month_name[month]} {year}', 0, 1, 'C')
        pdf.ln(10)
        
        # Statistics section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Key Statistics', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        stats = [
            f'Total Supporters: {analysis_data["total_supporters"]}',
            f'Unique Supporters: {analysis_data["unique_supporters"]}',
            f'Total Donations: {analysis_data["total_donations"]}',
            f'Total Revenue: ${analysis_data["total_revenue"]:,.2f}',
            f'Average Donation: ${analysis_data["average_donation"]:,.2f}'
        ]
        
        for stat in stats:
            pdf.cell(0, 8, stat, 0, 1)
        
        pdf.ln(10)
        
        # Daily Revenue Chart
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Daily Revenue', 0, 1)
        pdf.image(daily_revenue_img, x=10, y=None, w=190)
        pdf.ln(10)
        
        # Top Supporters Section
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top 10 Supporters', 0, 1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(60, 10, 'Supporter Name', 1)
        pdf.cell(50, 10, 'Total Donated', 1)
        pdf.cell(40, 10, 'Donation Count', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for supporter in analysis_data['top_supporters']:
            pdf.cell(60, 8, supporter['name'], 1)
            pdf.cell(50, 8, f'${supporter["total_donated"]:,.2f}', 1)
            pdf.cell(40, 8, str(supporter['donation_count']), 1)
            pdf.ln()
        
        # Top Supporters Chart
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top Supporters Visualization', 0, 1)
        pdf.image(top_supporters_img, x=10, y=None, w=190)
        
        # Output file
        filename = f"donation_report_{year}_{month:02d}.pdf"
        pdf.output(filename)
        return filename


def main():
    parser = argparse.ArgumentParser(description='Generate monthly donation report')
    parser.add_argument('--token', required=True, help='API access token')
    parser.add_argument('--year', type=int, required=True, help='Year to generate report for')
    parser.add_argument('--month', type=int, required=True, help='Month to generate report for (1-12)')
    parser.add_argument('--api-url', default='https://api.donationplatform.com', 
                       help='Base URL for the donation platform API')
    
    args = parser.parse_args()
    
    if not (1 <= args.month <= 12):
        print("Error: Month must be between 1 and 12")
        sys.exit(1)
    
    # Validate date
    try:
        datetime(args.year, args.month, 1)
    except ValueError:
        print(f"Error: Invalid date {args.year}-{args.month}")
        sys.exit(1)
    
    print(f"Generating donation report for {calendar.month_name[args.month]} {args.year}...")
    
    # Initialize the report generator
    generator = DonationReportGenerator(args.token, args.api_url)
    
    try:
        # Get donations for the month
        donations = generator.get_donations_for_month(args.year, args.month)
        print(f"Retrieved {len(donations)} donations")
        
        # Analyze the data
        analysis = generator.analyze_donations(donations)
        print("Analysis complete")
        
        # Create visualizations
        daily_revenue_img, top_supporters_img = generator.create_visualizations(analysis, args.year, args.month)
        print(f"Visualizations created: {daily_revenue_img}, {top_supporters_img}")
        
        # Generate PDF report
        pdf_filename = generator.generate_pdf_report(analysis, args.year, args.month, 
                                                     daily_revenue_img, top_supporters_img)
        print(f"Report generated successfully: {pdf_filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()