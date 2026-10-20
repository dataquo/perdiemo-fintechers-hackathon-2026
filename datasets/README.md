# Datasets

This folder contains datasets downloaded from the hackathon S3 bucket and synthetic demo documents.

## Source

```
s3://ai-hackathon-datasets-422928733782/
```

Downloaded: 2026-10-19

## Contents

### CNB/ (Czech National Bank - Track 5)
- `clients.csv` - 5,493 synthetic clients with AML risk scores, PEP flags
- `transactions.csv` - ~400,000 synthetic transactions (July 2026)

### MerchantKYB/ (Tapaya - Track 4)
- Merchant application forms, UBO declarations, checklists
- 8 PDF documents for KYB intake testing

### MostlyRIght/ (EU Financial Firms - Tracks 1,4,5)
- EU financial firm licences and regulator warnings
- 10,500+ records for compliance checking

## Usage

```python
import pandas as pd

# Load CNB data
clients = pd.read_csv("datasets/CNB/clients.csv", sep=";")
transactions = pd.read_csv("datasets/CNB/transactions.csv", sep=";")

# Join on client ID
df = transactions.merge(clients, on="client ID")
```

## Note

All data is synthetic - no real PII or client information.
