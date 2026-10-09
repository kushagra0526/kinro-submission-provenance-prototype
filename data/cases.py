"""14 invented small-business insurance conversations, the submission that would go to carriers, and the planted issues.

Roles: "user" = the business owner (directly or quoted by their assistant), "agent" = the user's own AI assistant relaying
over MCP, "leo" = the broker's advisor. A leo turn starting with "QUOTE" is a quote being shown.
Nothing here is a real business, quote or carrier.
"""

TODAY_YEAR = 2026

CASES = [
    {"id": "K01", "lines": ["GL"], "assumed": ["coverage_start", "gl_limits"],
     "turns": [
         ("user", "I run a residential painting company in Austin, Texas, zip 78704. Been in business since 2018."),
         ("leo", "Thanks! Roughly what's your annual revenue, and any claims in the last 3 years?"),
         ("user", "Revenue was about $420k last year. No claims ever."),
         ("leo", "Do you or your crew ever work on roofs, and how tall are the buildings you paint?"),
         ("user", "We never go on roofs. Houses only, two stories max. And we don't use subs, all our own guys."),
         ("leo", "QUOTE ready: $142/month. I assumed a start date of Nov 1 and 1M/2M limits."),
     ],
     "submission": {"operations": "residential interior and exterior painting", "class": "Painting - residential", "state": "TX", "zip": "78704",
                    "years_in_business": 8, "annual_revenue": 420000, "prior_claims_3y": 0, "roofing_work": False, "max_stories": 2,
                    "subcontractor_cost": 0, "coverage_start": "2026-11-01", "gl_limits": "1M/2M"}},

    {"id": "K02", "lines": ["GL", "WC"], "assumed": ["coverage_start"],
     "turns": [
         ("agent", "My user owns a taqueria in Phoenix, Arizona (85004) and wants general liability and workers' comp."),
         ("leo", "Happy to help. How long have they been open, annual sales, and how many employees?"),
         ("user", "Open since 2021. Sales around $1.1M. 9 employees, payroll is $310k."),
         ("agent", "To confirm what my user said: payroll is $310k and 9 employees."),
         ("leo", "Do they serve alcohol, and do they deliver?"),
         ("user", "Beer only, maybe 8% of sales. No deliveries, pickup and DoorDash only, and no claims in 3 years."),
         ("leo", "QUOTE ready: GL $96/month. Workers' comp needs a licensed agent to finish; start assumed Nov 1."),
     ],
     "submission": {"operations": "counter-service Mexican restaurant", "class": "Restaurant - no bar", "state": "AZ", "zip": "85004",
                    "years_in_business": 5, "annual_revenue": 1100000, "employees": 9, "annual_payroll": 310000, "prior_claims_3y": 0,
                    "alcohol_sales_pct": 8, "deliveries": False, "coverage_start": "2026-11-01"}},

    {"id": "K03", "lines": ["GL"], "assumed": ["gl_limits"],
     "turns": [
         ("user", "I'm a handyman and carpenter in Columbus, Ohio 43215, mostly decks, trim and framing repairs. In business 6 years."),
         ("leo", "Got it. Revenue and any claims?"),
         ("user", "About $180k a year, one claim in 2024 for a damaged floor. We also do some roof repairs when customers ask, patching shingles mostly."),
         ("leo", "Thanks. Any subcontractors?"),
         ("user", "Nope, just me and my son."),
         ("leo", "QUOTE ready: $118/month."),
     ],
     "submission": {"operations": "handyman carpentry: decks, trim, framing repairs", "class": "Carpentry - residential", "state": "OH", "zip": "43215",
                    "years_in_business": 6, "annual_revenue": 180000, "prior_claims_3y": 1, "roofing_work": False, "subcontractor_cost": 0,
                    "gl_limits": "1M/2M"}},

    {"id": "K04", "lines": ["GL", "WC"], "assumed": [],
     "turns": [
         ("agent", "My user runs a cleaning business in Atlanta, Georgia, 30318. They want workers' comp and GL."),
         ("leo", "How many employees and what's the annual payroll?"),
         ("agent", "They didn't say, but a cleaning company that size probably has around 3 employees and maybe $150k payroll."),
         ("leo", "Thanks. Revenue and years in business?"),
         ("user", "We do about $260k in revenue, started in 2022. No claims."),
         ("leo", "QUOTE ready: GL $64/month; workers' comp estimate attached."),
     ],
     "submission": {"operations": "commercial office cleaning", "class": "Janitorial services", "state": "GA", "zip": "30318",
                    "years_in_business": 4, "annual_revenue": 260000, "employees": 3, "annual_payroll": 150000, "prior_claims_3y": 0}},

    {"id": "K05", "lines": ["WC"], "assumed": [],
     "turns": [
         ("user", "Landscaping company in Charlotte, North Carolina 28203, mowing and planting. 7 employees, payroll about $380k. Since 2016."),
         ("leo", "Any claims in the last 3 years, and annual revenue?"),
         ("user", "No claims. Revenue is $700k."),
         ("leo", "QUOTE ready: workers' comp estimate $1,240/month."),
         ("user", "That's too high. Make the payroll $240k and see what it comes to."),
     ],
     "submission": {"operations": "landscape maintenance: mowing, planting", "class": "Landscaping", "state": "NC", "zip": "28203",
                    "years_in_business": 10, "annual_revenue": 700000, "employees": 7, "annual_payroll": 240000, "prior_claims_3y": 0}},

    {"id": "K06", "lines": ["GL"], "assumed": ["coverage_start"],
     "turns": [
         ("user", "Boutique clothing store in Denver, Colorado 80206. Open since 2020, revenue $900k."),
         ("leo", "Any claims in the last 3 years?"),
         ("user", "No claims."),
         ("leo", "QUOTE ready: BOP $88/month."),
         ("user", "Correction, I misread my books: revenue was $600k last year, the $900k was our projection."),
     ],
     "submission": {"operations": "retail clothing boutique", "class": "Retail - clothing", "state": "CO", "zip": "80206",
                    "years_in_business": 6, "annual_revenue": 600000, "prior_claims_3y": 0, "coverage_start": "2026-11-01"}},

    {"id": "K07", "lines": ["GL"], "assumed": ["gl_limits"],
     "turns": [
         ("user", "General contractor doing kitchen and bath remodels in Tampa, Florida 33606. Been in business 12 years, revenue $1.4M."),
         ("leo", "Do you use subcontractors?"),
         ("user", "I sub out the electrical and plumbing to licensed guys, everything else is my crew."),
         ("leo", "Claims in 3 years? Any roof work?"),
         ("user", "No claims, and no roofing."),
         ("leo", "QUOTE ready: $310/month."),
     ],
     "submission": {"operations": "residential kitchen and bath remodeling", "class": "Contractor - remodeling", "state": "FL", "zip": "33606",
                    "years_in_business": 12, "annual_revenue": 1400000, "prior_claims_3y": 0, "roofing_work": False, "subcontractor_cost": 0,
                    "gl_limits": "1M/2M"}},

    {"id": "K08", "lines": ["GL"], "assumed": [],
     "turns": [
         ("user", "Neighborhood pizza place in Pittsburgh, Pennsylvania, 15213. We've been open 15 years, sales about $850k."),
         ("leo", "How much of your sales is alcohol, and do you deliver?"),
         ("user", "About 35% of sales are beer and wine, we have a small bar. No delivery."),
         ("leo", "Claims?"),
         ("user", "None in the last 3 years."),
         ("leo", "QUOTE ready: $121/month."),
     ],
     "submission": {"operations": "pizza restaurant with small bar", "class": "Restaurant - with bar", "state": "PA", "zip": "15213",
                    "years_in_business": 15, "annual_revenue": 850000, "prior_claims_3y": 0, "alcohol_sales_pct": 10, "deliveries": False}},

    {"id": "K09", "lines": ["GL"], "assumed": ["gl_limits", "hnoa"],
     "turns": [
         ("user", "I run a catering kitchen in Portland, Oregon 97214. Open since 2019, about $500k revenue, no alcohol."),
         ("leo", "Do you deliver?"),
         ("user", "Yes, I deliver catering orders myself in my own van, and two staff use their cars sometimes."),
         ("leo", "Claims?"),
         ("user", "No claims."),
         ("leo", "QUOTE ready: $102/month."),
     ],
     "submission": {"operations": "catering kitchen", "class": "Caterer", "state": "OR", "zip": "97214", "years_in_business": 7,
                    "annual_revenue": 500000, "prior_claims_3y": 0, "alcohol_sales_pct": 0, "deliveries": True, "hnoa": False, "gl_limits": "1M/2M"}},

    {"id": "K10", "lines": ["GL"], "assumed": ["coverage_start"],
     "turns": [
         ("user", "Barbershop in Detroit, Michigan 48226, two chairs, open since 2017. Revenue around $210k."),
         ("leo", "QUOTE ready: $58/month."),
     ],
     "submission": {"operations": "barbershop", "class": "Barber shop", "state": "MI", "zip": "48226", "years_in_business": 9,
                    "annual_revenue": 210000, "prior_claims_3y": 0, "coverage_start": "2026-11-01"}},

    {"id": "K11", "lines": ["GL"], "assumed": ["gl_limits"],
     "turns": [
         ("user", "Lawn care business in Nashville, Tennessee 37206, mowing and leaf cleanup, since 2020. Revenue $230k, no claims."),
         ("leo", "Anything besides mowing and cleanup?"),
         ("user", "We also do tree removal a few times a month, that's the money maker in winter."),
         ("leo", "QUOTE ready: $74/month."),
     ],
     "submission": {"operations": "lawn mowing and leaf cleanup", "class": "Lawn care", "state": "TN", "zip": "37206", "years_in_business": 6,
                    "annual_revenue": 230000, "prior_claims_3y": 0, "gl_limits": "1M/2M"}},

    {"id": "K12", "lines": ["GL"], "assumed": ["coverage_start", "hnoa", "gl_limits"],
     "turns": [
         ("agent", "My user has a dog grooming salon in San Diego, California, 92104. Open since 2015, revenue $340k, no claims."),
         ("leo", "Thanks. I'll quote 1M/2M limits starting Nov 1 and include hired and non-owned auto; tell me if they'd like different."),
         ("leo", "QUOTE ready: $69/month."),
     ],
     "submission": {"operations": "pet grooming salon", "class": "Pet grooming", "state": "CA", "zip": "92104", "years_in_business": 11,
                    "annual_revenue": 340000, "prior_claims_3y": 0, "coverage_start": "2026-11-01", "hnoa": True, "gl_limits": "1M/2M"}},

    {"id": "K13", "lines": ["WC"], "assumed": [],
     "turns": [
         ("user", "HVAC contractor in Dallas, Texas 75201, since 2014. It's me plus four guys, payroll $260k, revenue $900k."),
         ("leo", "Claims in 3 years?"),
         ("user", "One small workers' comp claim in 2023."),
         ("leo", "QUOTE ready: workers' comp estimate $890/month."),
     ],
     "submission": {"operations": "residential HVAC install and repair", "class": "HVAC contractor", "state": "TX", "zip": "75201",
                    "years_in_business": 12, "annual_revenue": 900000, "employees": 2, "annual_payroll": 260000, "prior_claims_3y": 1}},

    {"id": "K14", "lines": ["GL"], "assumed": ["gl_limits"],
     "turns": [
         ("user", "Window cleaning company in Chicago, Illinois 60607, since 2019, about $390k revenue."),
         ("leo", "How tall are the buildings you work on?"),
         ("user", "Mostly three-story walkups, sometimes 5 story buildings with a lift. No claims, no subs."),
         ("leo", "QUOTE ready: $133/month."),
     ],
     "submission": {"operations": "residential and commercial window cleaning", "class": "Window cleaning", "state": "IL", "zip": "60607",
                    "years_in_business": 7, "annual_revenue": 390000, "prior_claims_3y": 0, "max_stories": 3, "subcontractor_cost": 0,
                    "gl_limits": "1M/2M"}},
]

# planted issues: (case, field or rule, code)
TRUTH = [
    ("K03", "roofing_work", "OPS_CONFLICT"),
    ("K04", "employees", "INFERRED"),
    ("K04", "annual_payroll", "INFERRED"),
    ("K05", "annual_payroll", "CHANGED_AFTER_QUOTE"),
    ("K07", "subcontractor_cost", "OPS_CONFLICT"),
    ("K08", "alcohol_sales_pct", "CONTRADICTED"),
    ("K09", "hnoa", "COVERAGE_GAP"),
    ("K10", "prior_claims_3y", "UNSOURCED"),
    ("K11", "class", "CLASS_FIT"),
    ("K13", "employees", "CONTRADICTED"),
    ("K14", "max_stories", "CONTRADICTED"),
]
