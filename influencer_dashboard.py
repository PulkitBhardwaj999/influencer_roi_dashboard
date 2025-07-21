import streamlit as st
import pandas as pd

st.set_page_config(page_title="Influencer ROI Dashboard", layout="wide")

df_influencers = pd.read_csv("datasets/influencers.csv")
df_posts = pd.read_csv("datasets/posts.csv")
df_tracking = pd.read_csv("datasets/tracking_data.csv")
df_payouts = pd.read_csv("datasets/payouts.csv")

merged = df_tracking.merge(df_influencers, left_on="influencer_id", right_on="ID", how="left")
merged = merged.merge(df_payouts, on="influencer_id", how="left")

st.sidebar.title("🔍 Filters")
brand = st.sidebar.multiselect("Product", options=merged["product"].unique())
platform = st.sidebar.multiselect("Platform", options=merged["Platform"].unique())
category = st.sidebar.multiselect("Category", options=merged["Category"].unique())

filtered = merged.copy()
if brand:
    filtered = filtered[filtered["product"].isin(brand)]
if platform:
    filtered = filtered[filtered["Platform"].isin(platform)]
if category:
    filtered = filtered[filtered["Category"].isin(category)]

st.title("📊 Influencer Marketing ROI Dashboard")

st.subheader("💡 Key Metrics")
total_revenue = filtered["revenue"].sum()
total_spend = filtered["total_payout"].sum()
roas = total_revenue / total_spend if total_spend else 0.0
roi = (total_revenue - total_spend) / total_spend if total_spend else 0.0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
kpi2.metric("Total Spend", f"₹{total_spend:,.0f}")
kpi3.metric("ROAS", f"{roas:.2f}")

st.subheader("🏆 Top Influencers by Revenue")
top_revenue = filtered.groupby("Name", as_index=False)["revenue"].sum().sort_values(by="revenue", ascending=False)
st.dataframe(top_revenue, use_container_width=True)

st.subheader("💰 Payout Tracking")
if "orders_y" in filtered.columns:
    filtered = filtered.rename(columns={"orders_y": "payout_orders"})
else:
    filtered["payout_orders"] = None
payout_table = filtered[["Name", "basis", "rate", "payout_orders", "total_payout"]].drop_duplicates()
payout_table = payout_table.rename(columns={"payout_orders": "orders"})
st.dataframe(payout_table, use_container_width=True)

st.download_button(
    "⬇️ Export as CSV",
    data=filtered.to_csv(index=False),
    file_name="campaign_data.csv"
)

st.subheader("📌 Automated Insights")
if not top_revenue.empty:
    best_rev_inf = top_revenue.iloc[0]["Name"]
    st.write(f"✅ **Best Influencer (Revenue):** {best_rev_inf}")

    roas_group = (
        filtered.groupby("Name")
        .apply(lambda x: x["revenue"].sum() / x["total_payout"].sum() if x["total_payout"].sum() else 0)
        .sort_values(ascending=False)
    )
    st.write(f"💡 **Best ROAS:** {roas_group.index[0]} ({roas_group.iloc[0]:.2f})")
    st.write(f"⚠️ **Lowest ROAS:** {roas_group.index[-1]} ({roas_group.iloc[-1]:.2f})")
else:
    st.info("No data available for current selections.")
