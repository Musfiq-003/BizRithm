"""
BizRithm Sample Dataset Generator
Run: python data/generate_samples.py
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
np.random.seed(42)


def generate_ecommerce_dataset(n=2000) -> pd.DataFrame:
    """Generate realistic e-commerce sales dataset."""
    dates = pd.date_range("2022-01-01", periods=n, freq="D")
    products = {
        "Electronics": {"base_price": 15000, "margin": 0.22},
        "Clothing": {"base_price": 2500, "margin": 0.38},
        "Food & Beverage": {"base_price": 800, "margin": 0.45},
        "Home & Garden": {"base_price": 3500, "margin": 0.30},
        "Sports & Fitness": {"base_price": 4200, "margin": 0.28},
        "Books & Stationery": {"base_price": 500, "margin": 0.50},
        "Beauty & Personal Care": {"base_price": 1800, "margin": 0.42},
    }
    regions = {
        "Dhaka": 0.34, "Chittagong": 0.22, "Rajshahi": 0.14,
        "Sylhet": 0.12, "Khulna": 0.10, "Mymensingh": 0.08,
    }
    channels = ["Online", "Mobile App", "Store", "Marketplace"]
    product_names = list(products.keys())
    region_names = list(regions.keys())

    rows = []
    for i, date in enumerate(dates):
        n_orders = np.random.poisson(8 + 3 * np.sin(2*np.pi*date.dayofyear/365))
        for _ in range(max(1, n_orders)):
            product = np.random.choice(product_names, p=[0.25,0.20,0.18,0.12,0.10,0.08,0.07])
            region = np.random.choice(region_names, p=list(regions.values()))
            p_info = products[product]
            price = p_info["base_price"] * np.random.uniform(0.8, 1.25)
            qty = np.random.randint(1, 15)
            revenue = price * qty
            rows.append({
                "order_id": f"ORD-{i:05d}-{len(rows):04d}",
                "date": date.strftime("%Y-%m-%d"),
                "product_category": product,
                "region": region,
                "channel": np.random.choice(channels, p=[0.45,0.30,0.15,0.10]),
                "quantity": qty,
                "unit_price": round(price, 2),
                "revenue": round(revenue, 2),
                "cost": round(revenue * (1 - p_info["margin"]), 2),
                "profit": round(revenue * p_info["margin"], 2),
                "profit_margin": round(p_info["margin"] * np.random.uniform(0.85, 1.15), 3),
                "customer_id": f"CUST-{np.random.randint(1000, 9999)}",
                "is_returned": int(np.random.random() < 0.05),
                "marketing_spend": round(np.random.uniform(200, 3000), 2),
                "customer_age_group": np.random.choice(["18-24","25-34","35-44","45-54","55+"],
                                                        p=[0.15,0.35,0.28,0.15,0.07]),
            })
    return pd.DataFrame(rows)


def generate_retail_dataset(n=1500) -> pd.DataFrame:
    """Generate retail store dataset."""
    rows = []
    stores = [f"Store-{i:03d}" for i in range(1, 21)]
    for i in range(n):
        date = datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 730))
        rows.append({
            "transaction_id": f"TXN-{i:06d}",
            "date": date.strftime("%Y-%m-%d"),
            "store_id": np.random.choice(stores),
            "product_sku": f"SKU-{np.random.randint(1000, 9999)}",
            "category": np.random.choice(["FMCG","Apparel","Electronics","Pharmacy","Fresh"]),
            "quantity_sold": np.random.randint(1, 50),
            "sale_price": round(np.random.uniform(50, 5000), 2),
            "cost_price": round(np.random.uniform(30, 4000), 2),
            "discount_pct": round(np.random.uniform(0, 30), 1),
            "footfall": np.random.randint(100, 2000),
            "weather": np.random.choice(["Sunny","Rainy","Cloudy","Hot"]),
            "is_holiday": int(np.random.random() < 0.12),
        })
    df = pd.DataFrame(rows)
    df["net_sales"] = df["sale_price"] * df["quantity_sold"] * (1 - df["discount_pct"]/100)
    df["gross_profit"] = df["net_sales"] - df["cost_price"] * df["quantity_sold"]
    return df


def generate_banking_dataset(n=1000) -> pd.DataFrame:
    """Generate banking transaction dataset."""
    rows = []
    for i in range(n):
        date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
        txn_type = np.random.choice(["Credit","Debit","Transfer","ATM"], p=[0.35,0.40,0.15,0.10])
        amount = round(np.random.lognormal(8, 1.5), 2)
        rows.append({
            "transaction_id": f"BNK-{i:07d}",
            "date": date.strftime("%Y-%m-%d"),
            "customer_id": f"CIF-{np.random.randint(10000, 99999)}",
            "transaction_type": txn_type,
            "amount": amount,
            "account_balance": round(np.random.uniform(1000, 500000), 2),
            "branch": np.random.choice(["Dhaka Main","Gulshan","Dhanmondi","Chittagong","Sylhet"]),
            "channel": np.random.choice(["Mobile","Web","ATM","Branch"], p=[0.40,0.30,0.20,0.10]),
            "status": np.random.choice(["Success","Failed","Pending"], p=[0.92,0.05,0.03]),
            "age_group": np.random.choice(["18-25","26-35","36-45","46-60","60+"], p=[0.15,0.35,0.30,0.15,0.05]),
            "is_fraud": int(np.random.random() < 0.02),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("[*] Generating BizRithm sample datasets...")
    output_dir = os.path.dirname(os.path.abspath(__file__))

    df_ecom = generate_ecommerce_dataset(2000)
    path = os.path.join(output_dir, "ecommerce_sales.csv")
    df_ecom.to_csv(path, index=False)
    print(f"[OK] E-commerce dataset: {len(df_ecom):,} rows -> {path}")

    df_retail = generate_retail_dataset(1500)
    path = os.path.join(output_dir, "retail_data.csv")
    df_retail.to_csv(path, index=False)
    print(f"[OK] Retail dataset: {len(df_retail):,} rows -> {path}")

    df_bank = generate_banking_dataset(1000)
    path = os.path.join(output_dir, "banking_transactions.csv")
    df_bank.to_csv(path, index=False)
    print(f"[OK] Banking dataset: {len(df_bank):,} rows -> {path}")

    print("\n[DONE] All datasets generated! Find them in the data/ folder.")
