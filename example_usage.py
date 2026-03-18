#!/usr/bin/env python3
"""
Example script showing how to use the Donation Report Generator
"""

from donation_report_generator import DonationReportGenerator
import os


def main():
    # Example usage of the donation report generator
    # In practice, you would get the token from environment variables or secure storage
    api_token = os.getenv('DONATION_API_TOKEN', 'your_api_token_here')
    
    # Initialize the generator
    generator = DonationReportGenerator(api_token)
    
    # Generate a report for January 2023 (as an example)
    year = 2023
    month = 1
    
    print(f"Generating donation report for {year}-{month:02d}...")
    
    try:
        # Get donations for the month
        donations = generator.get_donations_for_month(year, month)
        print(f"Retrieved {len(donations)} donations")
        
        # Analyze the data
        analysis = generator.analyze_donations(donations)
        print("Analysis complete:")
        print(f"  Total Supporters: {analysis['total_supporters']}")
        print(f"  Unique Supporters: {analysis['unique_supporters']}")
        print(f"  Total Revenue: ${analysis['total_revenue']:,.2f}")
        print(f"  Average Donation: ${analysis['average_donation']:,.2f}")
        
        # Create visualizations
        daily_revenue_img, top_supporters_img = generator.create_visualizations(analysis, year, month)
        print(f"Visualizations created: {daily_revenue_img}, {top_supporters_img}")
        
        # Generate PDF report
        pdf_filename = generator.generate_pdf_report(analysis, year, month, 
                                                     daily_revenue_img, top_supporters_img)
        print(f"Report generated successfully: {pdf_filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()