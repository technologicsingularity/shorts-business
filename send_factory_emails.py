#!/usr/bin/env python3
"""
Send factory outreach emails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
sender_email = "technologicsingularity@gmail.com"
password = "oh.B6m3xh_x8GEvu"  # From earlier

# Factory contacts
factories = [
    {
        "name": "Hucai Activewear",
        "email": "info@hcactivewear.com",  # Need to verify
        "website": "hcactivewear.com",
        "notes": "BSCI, OEKO-TEX certified. MOQ 200."
    },
    {
        "name": "Aolafree OEM", 
        "email": "sales@aolafree.com",  # Need to verify
        "website": "aolafree.com",
        "notes": "Flexible MOQ 150. Full customization."
    },
    {
        "name": "Goal Sportswear",
        "email": "contact@goaluniform.com",
        "website": "goaluniform.com", 
        "notes": "Specializes in spandex shorts."
    },
    {
        "name": "Foshan Dopoo Sportswear",
        "email": "dopoosports@163.com",  # From made-in-china
        "website": "dopoosports.en.made-in-china.com",
        "notes": "MOQ 100. Sample-based customization."
    },
    {
        "name": "Betteractive",
        "email": "info@betteractive.com",
        "website": "betteractive.com",
        "notes": "MOQ 100. OEM/ODM services."
    }
]

email_body = """Subject: Athletic Shorts Manufacturing Inquiry - Custom Design Project

Dear Manufacturing Team,

I am reaching out on behalf of a new athletic wear brand focused on premium running and training shorts. We are looking for a manufacturing partner for our initial production run.

PRODUCT SPECIFICATIONS:
- Style: Men's athletic/training shorts
- Inseam: 6 inches (15cm) and 7 inches (18cm) options
- Fabric: 4-way stretch, moisture-wicking
  - Composition: 82% Polyester / 18% Elastane
  - Weight: 140-160 GSM
  - Similar to performance knit fabrics

KEY FEATURES:
- Elastic waistband with internal drawcord
- High-placement zippered side pockets (2)
- Additional drop-in pocket for cards/keys
- Unlined design
- Flatlock seams for comfort
- Athletic tapered fit

INITIAL ORDER:
- First run: 500-1000 units
- Mix: 3 colorways (Black, Navy, Olive)
- Two sizes initially: M and L
- Target cost: $8-12 per unit FOB

We have detailed tech packs and fabric specifications ready to share. We are looking for a partner who can:
1. Source high-quality performance fabrics
2. Produce samples within 2-3 weeks
3. Handle full production with consistent quality
4. Meet compliance standards for US market

Could you please provide:
- MOQ and pricing for 500 and 1000 units
- Sample lead time and cost
- Production timeline
- Fabric sourcing capabilities
- Any certifications (OEKO-TEX, BSCI, etc.)

We are ready to move quickly and establish a long-term partnership.

Best regards,
Alita
Product Development
Email: technologicsingularity@gmail.com
"""

print("Factory Outreach List:")
print("=" * 60)
for i, factory in enumerate(factories, 1):
    print(f"{i}. {factory['name']}")
    print(f"   Email: {factory['email']}")
    print(f"   Website: {factory['website']}")
    print(f"   Notes: {factory['notes']}")
    print()

print("=" * 60)
print("\n⚠️ IMPORTANT: These emails need verification.")
print("Next step: Visit websites to find correct contact emails.")
print("\nReady to send emails once contacts are verified!")
