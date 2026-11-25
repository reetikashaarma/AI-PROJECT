from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from modules.data_loader import load_uploaded_file, detect_columns
from modules.preprocessing import clean_sales_data
from modules.sales_analysis import (calculate_kpis,monthly_revenue,product_performance,
    category_performance,regional_performance,descriptive_statistics,correlation_matrix,generate_findings)
from modules.forecasting import forecast_revenue
from modules.anomaly_detection import detect_revenue_anomalies
from modules.ai_insights import generate_ai_insights
from modules.report_generator import build_excel_report,build_pdf_report
from modules.project_health import build_health_report

st.set_page_config(page_title="AI Sales Intelligence",page_icon="📊",layout="wide")
st.markdown("""
<style>
.stApp{background:radial-gradient(ellipse at 15% 0%,#172743 0%,#0a1020 55%);color:#edf2fa}
[data-testid="stSidebar"]{background:#0d1729;border-right:1px solid #293b55}
.block-container{max-width:1500px;padding-top:1.7rem}
h1,h2,h3{color:#f4f7fc}
[data-testid="stMetric"]{background:linear-gradient(145deg,#17263e,#111b2e);border:1px solid #2a3b56;border-radius:14px;padding:15px}
.hero{background:linear-gradient(110deg,#1b3a52,#132239 60%,#1c3147);border:1px solid #31506a;border-radius:17px;padding:22px;margin-bottom:20px}
.kicker{color:#70d2df;font-size:.72rem;letter-spacing:.15em;font-weight:700}
.insight{background:#121f33;border:1px solid #293d59;border-left:3px solid #55c2d8;border-radius:9px;padding:12px;margin:7px 0}

/* Midnight Executive Analytics redesign */
[data-testid="stSidebar"] { background:#0D1728 !important; border-right:1px solid #263750 !important; }
[data-testid="stSidebar"] .block-container { padding:1.25rem .9rem 2rem .9rem !important; }
.nav-brand { padding:.35rem .25rem 1.15rem .25rem; border-bottom:1px solid #263750; margin-bottom:.9rem; }
.nav-brand-title { color:#f1f5fb; font-weight:750; font-size:1.02rem; letter-spacing:.035em; }
.nav-brand-sub { color:#91a0b7; font-size:.76rem; margin-top:.35rem; }
.nav-group { color:#72849d; font-size:.66rem; font-weight:700; letter-spacing:.14em; margin:1.25rem 0 .42rem .35rem; }
[data-testid="stSidebar"] .stButton > button { width:100%; text-align:left; justify-content:flex-start; min-height:2.35rem; border:1px solid transparent !important; background:transparent !important; color:#b9c6d8 !important; border-radius:9px !important; padding:.45rem .65rem !important; font-size:.84rem !important; font-weight:500 !important; }
[data-testid="stSidebar"] .stButton > button:hover { background:#17263b !important; border-color:#263750 !important; color:#f1f5fb !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] { background:linear-gradient(100deg,rgba(66,198,213,.18),rgba(66,198,213,.07)) !important; border:1px solid rgba(66,198,213,.32) !important; color:#66d7e2 !important; }
.sidebar-dataset { margin-top:1rem; background:#142c2a; border:1px solid #24524a; border-radius:12px; padding:13px; }
.sidebar-dataset-label { color:#9bbab2; font-size:.7rem; }
.sidebar-dataset-value { color:#50d9ae; font-size:1.45rem; font-weight:750; margin-top:3px; }
.sidebar-dataset-status { color:#50d9ae; font-size:.72rem; margin-top:2px; }
.page-eyebrow { color:#6ecbd8; font-size:.68rem; font-weight:750; letter-spacing:.16em; margin-bottom:.35rem; }
.page-title { color:#f1f5fb; font-size:1.85rem; font-weight:750; letter-spacing:-.035em; margin:0; }
.page-subtitle { color:#91a0b7; font-size:.9rem; margin-top:.35rem; margin-bottom:1.2rem; }
.kpi-card { background:linear-gradient(145deg,#15243a,#111c2e); border:1px solid #263750; border-radius:15px; padding:17px 18px; min-height:116px; }
.kpi-label { color:#91a0b7; font-size:.76rem; font-weight:600; }
.kpi-value { color:#f1f5fb; font-size:1.55rem; font-weight:750; letter-spacing:-.025em; margin-top:9px; }
.kpi-icon { float:right; color:#42c6d5; font-size:1.05rem; }
.panel { background:#111d30; border:1px solid #263750; border-radius:15px; padding:16px; }

</style>
""",unsafe_allow_html=True)

def money(v):
    return "N/A" if v is None else f"{v:,.2f}"

def hero(title,subtitle,kicker="SALES INTELLIGENCE"):
    st.markdown(f'<div class="hero"><div class="kicker">{kicker}</div><h2>{title}</h2><div>{subtitle}</div></div>',unsafe_allow_html=True)

def explain_chart(title, meaning, takeaway):
    st.markdown(f"""
    <div style="background:#14243a;border:1px solid #2b405b;border-left:4px solid #42c6d5;border-radius:10px;padding:13px 16px;margin:4px 0 20px 0">
      <div style="color:#66d7e2;font-size:.72rem;font-weight:750;letter-spacing:.06em">{title}</div>
      <div style="color:#e8eef7;font-size:.88rem;margin-top:5px">{meaning}</div>
      <div style="color:#b6c6d9;font-size:.84rem;margin-top:5px"><b>What this tells us:</b> {takeaway}</div>
    </div>
    """, unsafe_allow_html=True)

def plain_money(value):
    if value is None or pd.isna(value): return "not available"
    return f"{value:,.2f}"

def trend_sentence(values, label="sales"):
    vals=pd.to_numeric(pd.Series(values),errors="coerce").dropna()
    if len(vals)<2: return "There is not enough information to compare months."
    first,last=float(vals.iloc[0]),float(vals.iloc[-1])
    if first==0: return f"{label.capitalize()} started at zero, so percentage change is not reliable."
    pct=(last-first)/abs(first)*100
    if pct>2: return f"{label.capitalize()} ended about {pct:.1f}% higher than it started."
    if pct<-2: return f"{label.capitalize()} ended about {abs(pct):.1f}% lower than it started."
    return f"{label.capitalize()} stayed close to its starting level."

with st.sidebar:
    st.markdown("""
    <div class="nav-brand">
      <div class="nav-brand-title">◈ SALES INTELLIGENCE</div>
      <div class="nav-brand-sub">BUSINESS ANALYTICS PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)
    nav_groups = [
        ("BUSINESS OVERVIEW", [("Overview","⌂"),("Revenue Analysis","↗"),("Product Performance","▦"),("Category & Region","◫"),("Statistical Analysis","∿")]),
        ("PREDICTIVE ANALYTICS", [("Forecasting","⌁"),("Anomaly Detection","⌕"),("AI Insights","✧")]),
        ("REPORTS & SETTINGS", [("Reports & Export","▤"),("Project Health","◉"),("Upload Dataset","⇧")]),
    ]
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Overview"
    for group_name, items in nav_groups:
        st.markdown(f'<div class="nav-group">{group_name}</div>', unsafe_allow_html=True)
        for label, glyph in items:
            selected = st.session_state.active_page == label
            if st.button(f"{glyph}   {label}", key=f"nav_{label}", type="primary" if selected else "secondary"):
                st.session_state.active_page = label
    page = st.session_state.active_page
    st.divider()
    if "clean_sales_df" in st.session_state:
        row_count = len(st.session_state.clean_sales_df)
        st.markdown(
            f'<div class="sidebar-dataset"><div class="sidebar-dataset-label">DATASET CONNECTED</div>'
            f'<div class="sidebar-dataset-value">{row_count:,}</div>'
            f'<div class="sidebar-dataset-status">● Prepared records</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="sidebar-dataset"><div class="sidebar-dataset-label">DATASET STATUS</div>'
            '<div class="sidebar-dataset-value">Not connected</div>'
            '<div class="sidebar-dataset-status">Upload a file to begin</div></div>',
            unsafe_allow_html=True)
    st.caption("MIDNIGHT EXECUTIVE · V1.0")


st.markdown('<div class="page-eyebrow">SALES INTELLIGENCE WORKSPACE</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">AI Sales Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Explore performance, forecast revenue and investigate unusual patterns.</div>', unsafe_allow_html=True)

if page=="Upload Dataset" or "clean_sales_df" not in st.session_state:
    hero("Import your sales data","Upload a CSV or Excel workbook, then verify the detected columns.","DATA MANAGEMENT")
    uploaded=st.file_uploader("Choose a sales dataset",type=["csv","xlsx","xls"])
    if uploaded:
        try:
            raw,sheet=load_uploaded_file(uploaded)
            st.success(f"Loaded {uploaded.name} · {sheet} · {len(raw):,} rows")
            st.dataframe(raw.head(15),use_container_width=True)
            detected=detect_columns(raw.columns)
            st.subheader("Confirm column mapping")
            choices=["(Not available)"]+list(raw.columns)
            labels=[("order_date","Order date *"),("sales","Sales / revenue *"),("order_id","Order ID"),
                    ("product","Product name"),("category","Category"),("quantity","Quantity"),
                    ("profit","Profit"),("region","Region"),("unit_price","Unit price"),("cost_price","Cost price")]
            mapping={}
            cols=st.columns(2)
            for i,(key,label) in enumerate(labels):
                guess=detected.get(key)
                default=guess if guess in raw.columns else "(Not available)"
                with cols[i%2]:
                    selected=st.selectbox(label,choices,index=choices.index(default),key=f"mapping_{key}")
                mapping[key]=None if selected=="(Not available)" else selected
            if st.button("Validate and prepare dataset",type="primary"):
                try:
                    cleaned,quality=clean_sales_data(raw,mapping)
                    st.session_state.clean_sales_df=cleaned
                    st.session_state.cleaning_report=quality
                    st.session_state.pop("phase_forecast",None)
                    st.session_state.pop("phase_anomalies",None)
                    st.session_state.pop("phase_insights",None)
                    st.success("Dataset prepared successfully.")
                    st.json(quality)
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not process dataset: {exc}")
        except Exception as exc: st.error(f"Could not load dataset: {exc}")
    st.stop()

df=st.session_state.clean_sales_df.copy()
with st.expander("Change date, category or region filters",expanded=False):
    min_date,max_date=df.order_date.min().date(),df.order_date.max().date()
    date_range=st.date_input("Order date range",value=(min_date,max_date),min_value=min_date,max_value=max_date)
    filtered=df.copy()
    if isinstance(date_range,tuple) and len(date_range)==2:
        filtered=filtered[(filtered.order_date.dt.date>=date_range[0])&(filtered.order_date.dt.date<=date_range[1])]
    c1,c2=st.columns(2)
    with c1:
        if "category" in filtered:
            vals=sorted(filtered.category.dropna().astype(str).unique())
            chosen=st.multiselect("Category",vals,default=vals)
            filtered=filtered[filtered.category.astype(str).isin(chosen)]
    with c2:
        if "region" in filtered:
            vals=sorted(filtered.region.dropna().astype(str).unique())
            chosen=st.multiselect("Region",vals,default=vals)
            filtered=filtered[filtered.region.astype(str).isin(chosen)]
if filtered.empty:
    st.warning("No records match these filters.")
    st.stop()

k=calculate_kpis(filtered)
monthly=monthly_revenue(filtered)
products=product_performance(filtered)
categories=category_performance(filtered)
regions=regional_performance(filtered)

if page=="Overview":
    hero("Your sales at a glance","The main numbers and trends from the data you selected.","BUSINESS OVERVIEW")
    st.markdown("### The numbers that matter")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Money from sales",money(k["total_revenue"]))
    c2.metric("Orders",f'{k["total_orders"]:,}')
    c3.metric("Profit",money(k["total_profit"]))
    c4.metric("Average order value",money(k["average_order_value"]))
    st.caption("These figures use the filters selected above. Profit is shown only when your file contains profit data.")

    st.markdown("### How sales changed over time")
    if not monthly.empty:
        fig=px.line(monthly,x="month",y="sales",markers=True,template="plotly_dark",labels={"month":"Month","sales":"Sales"})
        fig.update_traces(line_color="#42C6D5",line_width=3,marker_size=7)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=20,b=5),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
        peak=monthly.loc[monthly.sales.idxmax()]
        low=monthly.loc[monthly.sales.idxmin()]
        explain_chart("How to read this graph","Each dot shows the money earned in one month. Higher dots mean more sales; lower dots mean fewer sales.",
                      f"The highest month was {peak['month']} ({plain_money(peak['sales'])}) and the lowest was {low['month']} ({plain_money(low['sales'])}). {trend_sentence(monthly['sales'],'Sales')}")
    st.markdown("### Which product groups bring in the most sales?")
    if not categories.empty:
        top_cat=categories.iloc[0]
        fig=px.bar(categories,x="category",y="sales",template="plotly_dark",labels={"category":"Product group","sales":"Sales"},
                   color="sales",color_continuous_scale=["#24506b","#42C6D5"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False,margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        explain_chart("How to read this graph","Each bar is a product group. A longer bar means that group earned more money.",
                      f"{top_cat['category']} is the biggest sales group, with {plain_money(top_cat['sales'])} in sales.")
    st.markdown("### Quick takeaways")
    for item in generate_findings(filtered): st.info(item)

elif page=="Revenue Analysis":
    hero("Revenue analysis","See how much money came in each month and whether sales went up or down.")
    st.markdown("### Sales by month")
    if not monthly.empty:
        fig=px.bar(monthly,x="month",y="sales",template="plotly_dark",labels={"month":"Month","sales":"Sales"})
        fig.update_traces(marker_color="#42C6D5")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        peak=monthly.loc[monthly.sales.idxmax()]
        explain_chart("What this graph shows","One bar represents one month. Taller bars mean more money came in during that month.",
                      f"Your best month was {peak['month']}, with {plain_money(peak['sales'])} in sales.")
    st.markdown("### Did sales rise or fall compared with the month before?")
    growth=monthly.dropna(subset=["mom_growth_pct"])
    if not growth.empty:
        fig=px.bar(growth,x="month",y="mom_growth_pct",template="plotly_dark",labels={"month":"Month","mom_growth_pct":"Change from previous month (%)"})
        fig.update_traces(marker_color=growth["mom_growth_pct"].apply(lambda x:"#50D9AE" if x>=0 else "#E68181"))
        fig.add_hline(y=0,line_dash="dot",line_color="#91A0B7")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        latest=float(growth.iloc[-1]["mom_growth_pct"])
        takeaway=(f"Sales increased by {latest:.1f}% in the latest month." if latest>0 else
                  f"Sales decreased by {abs(latest):.1f}% in the latest month." if latest<0 else
                  "Sales stayed almost the same in the latest month.")
        explain_chart("How to read this graph","Bars above zero mean sales increased. Bars below zero mean sales decreased.",takeaway)
    with st.expander("See the monthly sales numbers"):
        st.dataframe(monthly,use_container_width=True,hide_index=True)

elif page=="Product Performance":
    hero("Product performance","Find out which products bring in the most money.")
    if products.empty:
        st.info("Your file does not contain product names. Add a Product Name column to use this page.")
    else:
        n=st.slider("How many products should we show?",1,min(20,len(products)),min(8,len(products)))
        shown=products.head(n).sort_values("sales",ascending=True)
        fig=px.bar(shown,x="sales",y="product",orientation="h",template="plotly_dark",labels={"sales":"Sales","product":"Product"})
        fig.update_traces(marker_color="#42C6D5")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5),yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True)
        best=products.iloc[0]
        explain_chart("How to read this graph","Each bar represents one product. Longer bars mean that product earned more money.",
                      f"{best['product']} is the top product in the selected data, with {plain_money(best['sales'])} in sales.")
        with st.expander("See product details and figures"):
            st.dataframe(products,use_container_width=True,hide_index=True)

elif page=="Category & Region":
    hero("Categories and regions","Compare product groups and the places where sales happen.")
    st.markdown("### Sales by product group")
    if not categories.empty:
        fig=px.bar(categories,x="category",y="sales",template="plotly_dark",labels={"category":"Product group","sales":"Sales"})
        fig.update_traces(marker_color="#42C6D5")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        best=categories.iloc[0]
        explain_chart("What this graph means","Each bar is a product group. A taller bar means that group made more sales.",f"{best['category']} has the highest sales among the groups shown.")
    else: st.info("No category information is available.")
    st.markdown("### Sales by region")
    if not regions.empty:
        fig=px.bar(regions,x="region",y="sales",template="plotly_dark",labels={"region":"Region","sales":"Sales"})
        fig.update_traces(marker_color="#8B7CF6")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        best=regions.iloc[0]
        explain_chart("What this graph means","Each bar is a sales region. A taller bar means more money came from that region.",f"{best['region']} is the highest-selling region in the selected data.")
    else: st.info("No region information is available.")
    with st.expander("See the full category and region tables"):
        st.dataframe(categories,use_container_width=True,hide_index=True)
        st.dataframe(regions,use_container_width=True,hide_index=True)

elif page=="Statistical Analysis":
    hero("Understanding the numbers","A simple look at typical values and how sales figures move together.")
    st.markdown("### Summary of your sales data")
    st.write("This table gives a quick summary. The average is the usual value. The minimum and maximum show the smallest and largest values.")
    st.dataframe(descriptive_statistics(filtered),use_container_width=True)
    corr=correlation_matrix(filtered)
    if not corr.empty:
        st.markdown("### Do two things tend to change together?")
        fig=px.imshow(corr,text_auto=".2f",zmin=-1,zmax=1,template="plotly_dark",
                      labels={"x":"Measure","y":"Measure","color":"Relationship"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
        explain_chart("How to read this colour chart","Numbers close to +1 mean two measures often rise together. Numbers close to -1 mean when one rises, the other often falls. Numbers near 0 mean there is little clear connection.",
                      "This shows a pattern in the data. It does not prove that one thing causes another.")
    else: st.info("At least two number columns are needed to compare relationships.")

elif page=="Forecasting":
    hero("Revenue forecasting","Estimate the next 3, 6 or 12 months.")
    horizon=st.radio("Forecast horizon",[3,6,12],horizontal=True)
    if st.button("Generate forecast",type="primary"):
        try: st.session_state.phase_forecast=forecast_revenue(filtered,horizon)
        except Exception as exc: st.error(str(exc)); st.session_state.pop("phase_forecast",None)
    result=st.session_state.get("phase_forecast")
    if result:
        hist,pred=result["history"],result["forecast"]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hist.month,y=hist.actual_revenue,name="Actual",mode="lines+markers"))
        fig.add_trace(go.Scatter(x=pred.month,y=pred.predicted_revenue,name="Forecast",mode="lines+markers",line=dict(dash="dash")))
        fig.update_layout(template="plotly_dark",title="Actual vs forecast")
        st.plotly_chart(fig,use_container_width=True)
        explain_chart("How to read this forecast","The solid line shows sales already recorded. The dashed line shows the computer's estimate for future months.",
                      f"The estimate for the next {horizon} months is {plain_money(pred.predicted_revenue.sum())}. This is a guide, not a promise.")
        a,b=st.columns(2); a.metric("Estimated sales for this period",money(pred.predicted_revenue.sum())); b.metric("Forecast method",result["model_name"])
        with st.expander("What do the accuracy numbers mean?"):
            st.write(f"MAE: {result['evaluation']['mae']:,.2f}. This is roughly how far the model's fitted monthly estimates were from the actual sales.")
            st.write(f"RMSE: {result['evaluation']['rmse']:,.2f}. This is another error measure that gives bigger mistakes more weight.")
            st.caption(result["evaluation"]["message"])
        st.download_button("Download forecast CSV",pred.to_csv(index=False),"revenue_forecast.csv","text/csv")

elif page=="Anomaly Detection":
    hero("Unusual sales months","Find months when sales look very different from the usual pattern.")
    st.write("The system checks monthly sales and highlights months that look unusual. An unusual result is a reason to investigate, not proof that something is wrong.")
    contamination=st.slider("How many months should be flagged?",0.05,0.25,0.10,0.05,help="This setting controls how many months the model may mark as unusual.")
    if st.button("Check for unusual months",type="primary"):
        st.session_state.phase_anomalies=detect_revenue_anomalies(filtered,contamination)
    result=st.session_state.get("phase_anomalies")
    if result:
        st.metric("Months marked as unusual",result["anomaly_count"])
        st.info(result["message"])
        if not result["data"].empty:
            chart_data=result["data"].copy()
            fig=px.line(chart_data,x="month",y="revenue",markers=True,template="plotly_dark",labels={"month":"Month","revenue":"Sales"})
            flagged=chart_data[chart_data["is_anomaly"]]
            if not flagged.empty:
                fig.add_scatter(x=flagged["month"],y=flagged["revenue"],mode="markers",name="Unusual month",marker=dict(color="#F29E68",size=12,symbol="x"))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
            explain_chart("How to read this graph","The line shows sales month by month. Orange crosses mark months the system thinks look unusual.",
                          "Check those months for changes in demand, large orders, discounts, missing records or data-entry mistakes.")
        with st.expander("See the months marked by the system"):
            st.dataframe(result["data"],use_container_width=True,hide_index=True)
        st.download_button("Download results",result["data"].to_csv(index=False),"sales_anomalies.csv","text/csv")

elif page=="AI Insights":
    hero("What your sales data is telling you","Simple findings and practical ideas based on the numbers in your file.")
    st.caption("These notes are created from calculations in your data. They are not written by a human analyst or an online AI service.")
    if st.button("Generate insights",type="primary"): st.session_state.phase_insights=generate_ai_insights(filtered)
    result=st.session_state.get("phase_insights")
    if result:
        st.info(result["summary"])
        a,b=st.columns(2)
        with a:
            st.subheader("What we found")
            for x in result["insights"]: st.markdown(f'<div class="insight">📈 {x}</div>',unsafe_allow_html=True)
        with b:
            st.subheader("What you could do next")
            for x in result["recommendations"]: st.markdown(f'<div class="insight">💡 {x}</div>',unsafe_allow_html=True)
        rows=[{"Type":"Insight","Text":x} for x in result["insights"]]+[{"Type":"Recommendation","Text":x} for x in result["recommendations"]]
        st.download_button("Download insights CSV",pd.DataFrame(rows).to_csv(index=False),"sales_insights.csv","text/csv")

elif page=="Reports & Export":
    hero("Reports and export","Download reports based on the currently selected filters.")
    insights=st.session_state.get("phase_insights")
    if st.button("Generate insights for report"): insights=generate_ai_insights(filtered); st.session_state.phase_insights=insights
    if st.button("Prepare Excel workbook",type="primary"):
        try: st.session_state.phase_excel=build_excel_report(filtered,k,monthly,products,categories,regions,insights)
        except Exception as exc: st.error(str(exc))
    if st.session_state.get("phase_excel"):
        st.download_button("Download Excel report",st.session_state.phase_excel,"ai_sales_analytics.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if st.button("Prepare PDF report"):
        try: st.session_state.phase_pdf=build_pdf_report(k,monthly,products,categories,regions,insights)
        except Exception as exc: st.error(str(exc))
    if st.session_state.get("phase_pdf"):
        st.download_button("Download PDF report",st.session_state.phase_pdf,"ai_sales_analytics.pdf","application/pdf")
    st.download_button("Download filtered CSV",filtered.to_csv(index=False),"cleaned_sales_data.csv","text/csv")

elif page=="Project Health":
    hero("Project health","Check required packages, files and dataset fields.")
    report=build_health_report(".",filtered)
    a,b=st.columns(2); a.metric("Checks ready",report["ready_count"]); b.metric("Missing",report["missing_count"])
    st.success("All checks passed.") if report["overall_status"]=="Ready" else st.warning("Review missing items.")
    st.dataframe(pd.DataFrame(report["checks"]),use_container_width=True)
    st.download_button("Download health report",pd.DataFrame(report["checks"]).to_csv(index=False),"project_health.csv","text/csv")
