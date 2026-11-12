
import streamlit as st
import pandas as pd
import re
import os

from datetime import date, datetime
from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq


# ==========================================
# 1. INITIAL CONFIGURATION
# ==========================================

load_dotenv()

st.set_page_config(
    page_title="AI Real Estate Lease Analyzer",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 AI Real Estate Lease Analyzer")

st.write(
    "Upload, analyze and manage commercial lease documents using AI."
)

st.divider()


# ==========================================
# 2. PDF TEXT EXTRACTION
# ==========================================

def extract_text(pdf_file):

    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    # Workaround for the square currency character
    text = text.replace("■", "₹")

    return text


# ==========================================
# 3. EXTRACT LEASE DETAILS
# ==========================================

def find_value(text, label):

    pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return "Not Found"


# ==========================================
# 4. CONVERT RENT AND DEPOSIT TO NUMBERS
# ==========================================

def parse_amount(value):

    numbers = re.sub(
        r"[^0-9.]",
        "",
        value.replace(",", "")
    )

    return float(numbers) if numbers else None


# ==========================================
# 5. CONVERT DATE TEXT TO DATE FORMAT
# ==========================================

def parse_date(value):

    formats = [
        "%d-%m-%Y",
        "%d-%b-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value.strip(),
                fmt
            ).date()

        except ValueError:
            continue

    return None


# ==========================================
# 6. GROQ AI FUNCTION
# ==========================================

def ask_groq(system_prompt, user_prompt, max_tokens=2000):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "Groq API key not found. Check your .env file."
        )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.2,
        max_completion_tokens=max_tokens
    )

    return response.choices[0].message.content


# ==========================================
# 7. PDF UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📄 Upload your commercial lease PDF",
    type=["pdf"]
)


if uploaded_file is not None:

    try:

        text = extract_text(uploaded_file)

        if not text.strip():

            st.error(
                "No readable text found in this PDF."
            )

            st.stop()

        st.success(
            "PDF uploaded and processed successfully!"
        )


        # ==========================================
        # 8. AUTOMATIC INFORMATION EXTRACTION
        # ==========================================

        details = {

            "Landlord": find_value(text, "Landlord"),

            "Tenant": find_value(text, "Tenant"),

            "Property": find_value(text, "Property"),

            "Monthly Rent": find_value(text, "Monthly Rent"),

            "Security Deposit": find_value(
                text, "Security Deposit"
            ),

            "Lease Start Date": find_value(
                text, "Lease Start Date"
            ),

            "Lease End Date": find_value(
                text, "Lease End Date"
            ),

            "Annual Rent Increase": find_value(
                text, "Annual Rent Increase"
            )
        }


        details_text = "\n".join(
            f"{key}: {value}"
            for key, value in details.items()
        )


        # ==========================================
        # 9. LEASE INFORMATION TABLE
        # ==========================================

        st.subheader(
            "📋 Extracted Lease Information"
        )

        df = pd.DataFrame(
            list(details.items()),
            columns=["Field", "Extracted Value"]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # CSV DOWNLOAD

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            label="⬇️ Download Lease Details as CSV",

            data=csv,

            file_name="lease_details.csv",

            mime="text/csv"
        )


        st.divider()


        # ==========================================
        # 10. LEASE ANALYTICS DASHBOARD
        # ==========================================

        st.header(
            "📊 Lease Analytics Dashboard"
        )

        monthly_rent = parse_amount(
            details["Monthly Rent"]
        )

        deposit = parse_amount(
            details["Security Deposit"]
        )

        escalation = parse_amount(
            details["Annual Rent Increase"]
        )

        start_date = parse_date(
            details["Lease Start Date"]
        )

        end_date = parse_date(
            details["Lease End Date"]
        )


        if (
            monthly_rent is not None
            and deposit is not None
            and escalation is not None
            and start_date is not None
            and end_date is not None
            and end_date >= start_date
        ):

            # Calculate lease years
            number_of_years = (
                end_date.year - start_date.year + 1
            )

            rent_data = []

            for i in range(number_of_years):

                yearly_monthly_rent = (

                    monthly_rent
                    * (1 + escalation / 100) ** i

                )

                yearly_total = (
                    yearly_monthly_rent * 12
                )

                rent_data.append({

                    "Lease Year": (
                        f"Year {i + 1} "
                        f"({start_date.year + i})"
                    ),

                    "Monthly Rent (₹)": (
                        yearly_monthly_rent
                    ),

                    "Annual Rent (₹)": (
                        yearly_total
                    )

                })


            rent_df = pd.DataFrame(rent_data)

            total_rent = (
                rent_df["Annual Rent (₹)"].sum()
            )


            # ==========================================
            # 11. DASHBOARD METRICS
            # ==========================================

            col1, col2 = st.columns(2)

            col1.metric(
                "Starting Monthly Rent",
                f"₹{monthly_rent:,.2f}"
            )

            col2.metric(
                "Security Deposit",
                f"₹{deposit:,.2f}"
            )


            col3, col4 = st.columns(2)

            col3.metric(
                "Annual Rent Escalation",
                f"{escalation:g}%"
            )

            col4.metric(
                "Total Projected Rent",
                f"₹{total_rent:,.2f}"
            )


            st.divider()


            # ==========================================
            # 12. YEAR-WISE RENT BREAKDOWN
            # ==========================================

            st.subheader(
                "📅 Year-wise Rent Breakdown"
            )

            display_df = rent_df.copy()

            display_df["Monthly Rent (₹)"] = (
                display_df["Monthly Rent (₹)"].map(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            display_df["Annual Rent (₹)"] = (
                display_df["Annual Rent (₹)"].map(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


            # ==========================================
            # 13. RENT GROWTH CHART
            # ==========================================

            st.subheader(
                "📈 Annual Rent Growth"
            )

            chart_df = rent_df.set_index(
                "Lease Year"
            )

            st.bar_chart(
                chart_df["Annual Rent (₹)"]
            )


            st.divider()


            # ==========================================
            # 14. LEASE EXPIRY TRACKER
            # ==========================================

            st.subheader(
                "⏳ Lease Expiry Tracker"
            )

            remaining_days = (
                end_date - date.today()
            ).days


            st.write(
                f"**Lease Start:** "
                f"{start_date.strftime('%d %b %Y')}"
            )

            st.write(
                f"**Lease End:** "
                f"{end_date.strftime('%d %b %Y')}"
            )


            if remaining_days > 0:

                st.metric(
                    "Days Until Lease Expiry",
                    remaining_days
                )

            elif remaining_days == 0:

                st.warning(
                    "The lease expires today."
                )

            else:

                st.warning(
                    f"The lease expired "
                    f"{-remaining_days} days ago."
                )


            st.info(
                "Rent projections assume full 12-month "
                "lease years and annual compounding. "
                "Taxes, utilities and other charges "
                "are excluded."
            )

        else:

            st.warning(
                "Could not calculate the dashboard. "
                "Please check the extracted rent, deposit, "
                "escalation and lease dates."
            )


        st.divider()


        # ==========================================
        # 15. AI QUESTION-ANSWERING ASSISTANT
        # ==========================================

        st.subheader(
            "🤖 AI Lease Assistant"
        )

        question = st.text_input(

            "Ask a question about your lease",

            placeholder=(
                "Example: What is the monthly rent?"
            )

        )


        if st.button(
            "Ask AI",
            type="primary"
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                try:

                    with st.spinner(
                        "AI is analyzing your lease..."
                    ):

                        answer = ask_groq(

                            system_prompt=(

                                "You are a commercial real estate "
                                "lease analysis assistant. Answer "
                                "using the supplied lease text and "
                                "extracted details. Cross-check "
                                "the information. If sources disagree, "
                                "clearly identify the disagreement. "
                                "If information is missing, say so. "
                                "Do not invent contract terms. "
                                "You are not a lawyer."

                            ),

                            user_prompt=f"""

EXTRACTED LEASE DETAILS:

{details_text}


ORIGINAL LEASE DOCUMENT:

{text[:30000]}


USER QUESTION:

{question}

""",

                            max_tokens=2000

                        )


                    st.subheader(
                        "💡 AI Answer"
                    )

                    st.markdown(answer)


                except Exception as e:

                    st.error(
                        f"AI request failed: {e}"
                    )


        st.divider()


        # ==========================================
        # 16. AI LEASE RISK ANALYSIS
        # ==========================================

        st.subheader(
            "⚠️ AI Lease Risk Analysis"
        )


        if st.button(
            "Analyze Lease Risks"
        ):

            try:

                with st.spinner(
                    "AI is checking lease risks..."
                ):

                    risk_report = ask_groq(

                        system_prompt=(

                            "You are a commercial real estate "
                            "lease risk analysis assistant. "
                            "Identify missing clauses, incomplete "
                            "terms, ambiguous wording and potential "
                            "risks. Use only the supplied evidence. "
                            "Do not invent information. "
                            "Cross-check extracted details with "
                            "the original document. "
                            "Distinguish missing information from "
                            "actual risks. "
                            "Organize the report using headings "
                            "and bullet points. "
                            "This is not legal advice."

                        ),

                        user_prompt=f"""

EXTRACTED LEASE DETAILS:

{details_text}


ORIGINAL LEASE DOCUMENT:

{text[:30000]}


TASK:

Prepare a detailed lease risk report.

Include:

1. Missing or incomplete clauses.
2. Unclear or ambiguous terms.
3. Financial risks.
4. Tenant-related risks.
5. Landlord-related risks.
6. Important recommendations.
7. Overall risk assessment.

For every issue, explain why it matters.

Do not invent facts.

""",

                        max_tokens=3000

                    )


                st.subheader(
                    "🔍 Lease Risk Report"
                )

                st.markdown(risk_report)


            except Exception as e:

                st.error(
                    f"Risk analysis failed: {e}"
                )


        st.divider()


        # ==========================================
        # 17. COMPLETE EXTRACTED PDF TEXT
        # ==========================================

        with st.expander(
            "View Complete Extracted PDF Text"
        ):

            st.text_area(

                "Extracted PDF Content",

                text,

                height=300

            )


    except Exception as e:

        st.error(
            f"Error processing PDF: {e}"
        )


# ==========================================
# 18. FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Real Estate Lease Analyzer | "
    "Educational Project Prototype"
)
