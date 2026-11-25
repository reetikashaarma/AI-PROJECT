from io import BytesIO
from datetime import datetime
import pandas as pd

def build_excel_report(df,kpis,monthly,products,categories,regions,insights=None):
    output=BytesIO()
    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        pd.DataFrame([kpis]).to_excel(writer,sheet_name="KPI Summary",index=False)
        df.to_excel(writer,sheet_name="Cleaned Data",index=False)
        monthly.to_excel(writer,sheet_name="Monthly Revenue",index=False)
        products.to_excel(writer,sheet_name="Products",index=False)
        categories.to_excel(writer,sheet_name="Categories",index=False)
        regions.to_excel(writer,sheet_name="Regions",index=False)
        if insights:
            rows=[{"Type":"Insight","Text":x} for x in insights.get("insights",[])]
            rows += [{"Type":"Recommendation","Text":x} for x in insights.get("recommendations",[])]
            pd.DataFrame(rows).to_excel(writer,sheet_name="AI Insights",index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes="A2"
            ws.auto_filter.ref=ws.dimensions
            for cells in ws.columns:
                width=min(max(max((len(str(c.value)) if c.value is not None else 0 for c in cells[:200]),default=10)+2,12),40)
                ws.column_dimensions[cells[0].column_letter].width=width
    return output.getvalue()

def build_pdf_report(kpis,monthly,products,categories,regions,insights=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
    output=BytesIO()
    doc=SimpleDocTemplate(output,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=15*mm,bottomMargin=15*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SubBlue",parent=styles["Heading2"],textColor=colors.HexColor("#167d94")))
    story=[Paragraph("AI Sales Analytics Report",styles["Title"]),
           Paragraph("Generated "+datetime.now().strftime("%d %B %Y, %I:%M %p"),styles["Normal"]),Spacer(1,8)]
    rows=[["Metric","Value"]]+[[k,str(round(v,2) if isinstance(v,(int,float)) else v)] for k,v in kpis.items()]
    t=Table(rows,colWidths=[80*mm,80*mm],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324d")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("PADDING",(0,0),(-1,-1),6)]))
    story += [Paragraph("Key performance indicators",styles["SubBlue"]),t]
    def add_table(title,frame):
        if frame is None or frame.empty:return
        story.append(Paragraph(title,styles["SubBlue"]))
        f=frame.head(12)
        data=[list(f.columns)]+[[str(v)[:45] for v in row] for row in f.itertuples(index=False,name=None)]
        tab=Table(data,repeatRows=1)
        tab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324d")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTSIZE",(0,0),(-1,-1),7),("GRID",(0,0),(-1,-1),.3,colors.grey),("PADDING",(0,0),(-1,-1),4)]))
        story.append(tab)
    add_table("Monthly revenue",monthly)
    add_table("Product performance",products)
    add_table("Category performance",categories)
    add_table("Regional performance",regions)
    if insights:
        story.append(Paragraph("Insights and recommendations",styles["SubBlue"]))
        for item in insights.get("insights",[])+insights.get("recommendations",[]):
            story.append(Paragraph("• "+str(item),styles["BodyText"]))
    doc.build(story)
    return output.getvalue()
