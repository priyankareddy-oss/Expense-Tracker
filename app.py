import streamlit as st
import json
from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# ---------------------------------------------------------
# File Configuration
# ---------------------------------------------------------

DATA_FILE = Path(__file__).parent / "expenses.json"


# ---------------------------------------------------------
# JSON Functions
# ---------------------------------------------------------

def load_expenses():
    """Load expenses from the JSON file."""

    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (json.JSONDecodeError, OSError):
        return []


def save_expenses(expenses):
    """Save expenses to the JSON file."""

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()


# ---------------------------------------------------------
# Helper Function
# ---------------------------------------------------------

def get_next_id():
    """Generate a new ID for an expense."""

    if not st.session_state.expenses:
        return 1

    return max(
        expense["id"]
        for expense in st.session_state.expenses
    ) + 1


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #666666;
            margin-bottom: 30px;
        }

        .metric-card {
            padding: 15px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Title
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">💰 Expense Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Track, manage and understand your spending</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Choose an option:",
    [
        "Dashboard",
        "Add Expense",
        "Edit Expense",
        "Delete Expense"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.header("📊 Expense Dashboard")

    expenses = st.session_state.expenses

    # No expenses
    if not expenses:
        st.info("No expenses available. Add your first expense.")
        st.stop()

    # Convert data to DataFrame
    df = pd.DataFrame(expenses)

    # Convert date column
    df["date"] = pd.to_datetime(df["date"])

    # Total expense
    total_expenses = df["amount"].sum()

    # Number of expenses
    expense_count = len(df)

    # Average expense
    average_expense = df["amount"].mean()

    # -----------------------------------------------------
    # Summary Cards
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Total Expenses",
            f"₹{total_expenses:,.2f}"
        )

    with col2:
        st.metric(
            "🧾 Number of Expenses",
            expense_count
        )

    with col3:
        st.metric(
            "📌 Average Expense",
            f"₹{average_expense:,.2f}"
        )

    st.divider()

    # -----------------------------------------------------
    # Expense Table
    # -----------------------------------------------------

    st.subheader("📋 All Expenses")

    display_df = df[
        ["date", "category", "description", "amount"]
    ].copy()

    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")

    display_df["amount"] = display_df["amount"].apply(
        lambda x: f"₹{x:,.2f}"
    )

    display_df.columns = [
        "Date",
        "Category",
        "Description",
        "Amount"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------------------------------
    # Spending by Category
    # -----------------------------------------------------

    st.subheader("📂 Spending by Category")

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_pie = px.pie(
            category_data,
            names="category",
            values="amount",
            title="Expenses by Category",
            hole=0.4
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    with col2:

        fig_bar = px.bar(
            category_data,
            x="category",
            y="amount",
            title="Category-wise Spending",
            labels={
                "category": "Category",
                "amount": "Amount (₹)"
            }
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    # -----------------------------------------------------
    # Spending Trend
    # -----------------------------------------------------

    st.subheader("📈 Spending Trend")

    daily_data = (
        df.groupby("date")["amount"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    fig_line = px.line(
        daily_data,
        x="date",
        y="amount",
        markers=True,
        title="Daily Spending Trend",
        labels={
            "date": "Date",
            "amount": "Amount (₹)"
        }
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )


# =========================================================
# ADD EXPENSE
# =========================================================

elif page == "Add Expense":

    st.header("➕ Add New Expense")

    with st.form("add_expense_form"):

        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Bills",
                "Entertainment",
                "Health",
                "Other"
            ]
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch at college"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=1.0,
            format="%.2f"
        )

        submitted = st.form_submit_button(
            "💾 Add Expense"
        )

        if submitted:

            if amount <= 0:
                st.error(
                    "Amount must be greater than 0."
                )

            elif not description.strip():
                st.error(
                    "Please enter a description."
                )

            else:

                new_expense = {
                    "id": get_next_id(),
                    "date": expense_date.isoformat(),
                    "category": category,
                    "description": description.strip(),
                    "amount": float(amount)
                }

                st.session_state.expenses.append(
                    new_expense
                )

                save_expenses(
                    st.session_state.expenses
                )

                st.success(
                    "Expense added successfully!"
                )


# =========================================================
# EDIT EXPENSE
# =========================================================

elif page == "Edit Expense":

    st.header("✏️ Edit Expense")

    expenses = st.session_state.expenses

    if not expenses:

        st.info(
            "No expenses available to edit."
        )

    else:

        expense_options = {
            f'{expense["id"]} - '
            f'{expense["description"]} '
            f'(₹{expense["amount"]:.2f})':
            expense["id"]
            for expense in expenses
        }

        selected_expense = st.selectbox(
            "Select an expense:",
            list(expense_options.keys())
        )

        selected_id = expense_options[
            selected_expense
        ]

        selected = next(
            expense
            for expense in expenses
            if expense["id"] == selected_id
        )

        with st.form("edit_expense_form"):

            edited_date = st.date_input(
                "Date",
                value=date.fromisoformat(
                    selected["date"]
                )
            )

            categories = [
                "Food",
                "Travel",
                "Shopping",
                "Education",
                "Bills",
                "Entertainment",
                "Health",
                "Other"
            ]

            current_category = selected["category"]

            if current_category not in categories:
                categories.append(current_category)

            edited_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(
                    current_category
                )
            )

            edited_description = st.text_input(
                "Description",
                value=selected["description"]
            )

            edited_amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                value=float(selected["amount"]),
                step=1.0,
                format="%.2f"
            )

            update_button = st.form_submit_button(
                "💾 Update Expense"
            )

            if update_button:

                if edited_amount <= 0:

                    st.error(
                        "Amount must be greater than 0."
                    )

                elif not edited_description.strip():

                    st.error(
                        "Description cannot be empty."
                    )

                else:

                    selected["date"] = (
                        edited_date.isoformat()
                    )

                    selected["category"] = (
                        edited_category
                    )

                    selected["description"] = (
                        edited_description.strip()
                    )

                    selected["amount"] = (
                        float(edited_amount)
                    )

                    save_expenses(
                        st.session_state.expenses
                    )

                    st.success(
                        "Expense updated successfully!"
                    )


# =========================================================
# DELETE EXPENSE
# =========================================================

elif page == "Delete Expense":

    st.header("🗑️ Delete Expense")

    expenses = st.session_state.expenses

    if not expenses:

        st.info(
            "No expenses available to delete."
        )

    else:

        expense_options = {
            f'{expense["id"]} - '
            f'{expense["description"]} '
            f'(₹{expense["amount"]:.2f})':
            expense["id"]
            for expense in expenses
        }

        selected_expense = st.selectbox(
            "Select an expense:",
            list(expense_options.keys())
        )

        selected_id = expense_options[
            selected_expense
        ]

        st.warning(
            "This expense will be permanently deleted."
        )

        if st.button(
            "🗑️ Delete Expense",
            type="primary"
        ):

            st.session_state.expenses = [
                expense
                for expense in st.session_state.expenses
                if expense["id"] != selected_id
            ]

            save_expenses(
                st.session_state.expenses
            )

            st.success(
                "Expense deleted successfully!"
            )

            st.rerun()