# Monthly Donation Report Generator

A Python automation tool that generates professional monthly PDF reports for tracking donations and supporter contributions.

## Features

- Connects to donation platform API using access token
- Retrieves all supporter/donation data for a specified month
- Analyzes donation patterns and supporter behavior
- Creates visual charts (daily revenue, top supporters)
- Generates a comprehensive PDF report

## Key Statistics Tracked

- Total supporters & unique supporters
- Total donations received
- Total revenue earned
- Average donation amount
- Top 10 supporters ranking
- Daily revenue breakdown

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python donation_report_generator.py --token YOUR_API_TOKEN --year 2023 --month 1
```

Options:
- `--token`: Your API access token (required)
- `--year`: Year to generate report for (required)
- `--month`: Month to generate report for (1-12) (required)
- `--api-url`: Base URL for the donation platform API (optional, defaults to https://api.donationplatform.com)

### Example

```bash
python donation_report_generator.py --token abc123xyz --year 2023 --month 3
```

This will generate a report for March 2023.

### Programmatic Usage

```python
from donation_report_generator import DonationReportGenerator

# Initialize the generator
generator = DonationReportGenerator("your_api_token")

# Generate a report for January 2023
year = 2023
month = 1

# Get donations for the month
donations = generator.get_donations_for_month(year, month)

# Analyze the data
analysis = generator.analyze_donations(donations)

# Create visualizations
daily_revenue_img, top_supporters_img = generator.create_visualizations(analysis, year, month)

# Generate PDF report
pdf_filename = generator.generate_pdf_report(analysis, year, month, 
                                             daily_revenue_img, top_supporters_img)
```

## Dependencies

- Python 3.x
- requests
- matplotlib
- fpdf2

## Security

Store your API token securely. Consider using environment variables:

```python
import os
api_token = os.getenv('DONATION_API_TOKEN')
```

## Output

The tool generates:
- A professional PDF report with charts and statistics
- Visual graphs (bar charts for daily revenue & top supporters)
- Organized data presentation
- Temporary image files for charts (automatically cleaned up after PDF generation)

## Support

If you found this tool helpful, consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/taxak)
