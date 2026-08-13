import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

st.set_page_config(
    page_title="Data Analytics Agent",
    layout="wide"
)

st.title("Automated Data Analytics Agent")
st.write("Upload any CSV file and get instant analysis!")

st.markdown("---")

st.header("Step 1: Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    help="Upload any CSV or Excel file to begin analysis"
)

if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        df = pd.read_excel(uploaded_file)
        st.info("Excel file detected and loaded!")
    else:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                uploaded_file.seek(0) 
                df = pd.read_csv(uploaded_file, encoding='latin1')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252')


    st.success(f"File uploaded successfully!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", df.shape[0])

    with col2:
        st.metric("Total Columns", df.shape[1])

    with col3:
        st.metric("File Size", 
                  f"{uploaded_file.size / 1024:.1f} KB")

    st.markdown("---")

    st.header("Data Preview (First 5 Rows)")
    st.dataframe(df.head())

    st.header("Column Information")

    col_info = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.values,
        "Non-Null Count": df.count().values,
        "Null Count": df.isnull().sum().values
    })
    
    st.dataframe(col_info)

    st.markdown("---")
    st.header("Step 2: Data Cleaning Report")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Issues Found")

        missing_count = df.isnull().sum().sum()

        duplicate_count = df.duplicated().sum()

        st.metric("Missing Values", missing_count,
                  delta="needs fixing" if missing_count > 0 
                  else "all good!",
                  delta_color="inverse")

        st.metric("Duplicate Rows", duplicate_count,
                  delta="needs fixing" if duplicate_count > 0 
                  else "all good!",
                  delta_color="inverse")

    with col2:
        st.subheader("Auto Fix")

        df_clean = df.copy()

        df_clean = df_clean.drop_duplicates()

        numeric_cols = df_clean.select_dtypes(
            include=['float64', 'int64']
        ).columns

        for col in numeric_cols:
            df_clean[col].fillna(
                df_clean[col].median(), inplace=True
            )

        text_cols = df_clean.select_dtypes(
            include=['object']
        ).columns

        for col in text_cols:
            df_clean[col].fillna('Unknown', inplace=True)

        st.success(f"Removed {duplicate_count} duplicate rows")
        st.success(f"Filled {missing_count} missing values")
        st.success(f"Clean dataset ready!")
        st.metric("Clean Rows", df_clean.shape[0])

    st.markdown("---")
    st.header("Step 3: Data Profile Report")

    tab1, tab2, tab3 = st.tabs([
        "Statistical Summary",
        "Numeric Columns",
        "Text Columns"
    ])

    with tab1:
        st.subheader("Statistical Summary of Your Data")
        st.write("This shows min, max, average for all number columns:")
        st.dataframe(df_clean.describe().round(2))

    with tab2:
        st.subheader("Numeric Column Details")

        for col in numeric_cols:
            with st.expander(f"{col}"):
                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric("Min", 
                              f"{df_clean[col].min():.2f}")
                with c2:
                    st.metric("Max", 
                              f"{df_clean[col].max():.2f}")
                with c3:
                    st.metric("Average", 
                              f"{df_clean[col].mean():.2f}")
                with c4:
                    st.metric("Median", 
                              f"{df_clean[col].median():.2f}")

    with tab3:
        st.subheader("Text Column Details")

        for col in text_cols:
            with st.expander(f"{col}"):
                c1, c2 = st.columns(2)

                with c1:
                    st.metric("Unique Values",
                              df_clean[col].nunique())

                with c2:
                    st.metric("Most Common",
                              df_clean[col].mode()[0])
                    
                st.write("Top 5 most common values:")
                top5 = df_clean[col].value_counts().head()
                st.dataframe(top5)

    st.markdown("---")
    st.header("Step 4: Auto-Generated KPIs")
    st.write("Your key business metrics — automatically calculated!")

    kpi_cols = df_clean.select_dtypes(
        include=['float64', 'int64']
    ).columns.tolist()

    if len(kpi_cols) == 0:
        st.warning("No numeric columns found for KPI generation!")

    else:
        for i in range(0, len(kpi_cols), 3):
            group = kpi_cols[i:i+3]

            cols = st.columns(3)

            for j, kpi_col in enumerate(group):
                with cols[j]:
                    total = df_clean[kpi_col].sum()

                    average = df_clean[kpi_col].mean()

                    maximum = df_clean[kpi_col].max()

                    minimum = df_clean[kpi_col].min()

                    st.subheader(f"{kpi_col}")
                    st.metric("Total", f"{total:,.2f}")
                    st.metric("Average", f"{average:,.2f}")
                    st.metric("Maximum", f"{maximum:,.2f}")
                    st.metric("Minimum", f"{minimum:,.2f}")
                    st.markdown("---")

    st.markdown("---")
    st.header("Smart Highlights")
    st.write("Key findings automatically detected from your data:")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Highest Values")

        for col in kpi_cols[:4]:
            max_val = df_clean[col].max()
            max_idx = df_clean[col].idxmax()

            st.info(
                f"**{col}** peaks at "
                f"**{max_val:,.2f}** "
                f"(row {max_idx})"
            )

    with col2:
        st.subheader("Lowest Values")

        for col in kpi_cols[:4]:
            min_val = df_clean[col].min()
            min_idx = df_clean[col].idxmin()

            st.warning(
                f"**{col}** drops to "
                f"**{min_val:,.2f}** "
                f"(row {min_idx})"
            )

    st.markdown("---")
    st.subheader("Column Relationships")
    st.write(
        "How strongly are your numeric columns related? "
        "(1.0 = perfect relationship, 0 = no relationship)"
    )

    if len(kpi_cols) > 1:
        correlation = df_clean[kpi_cols].corr().round(2)
        st.dataframe(correlation)
    else:
        st.info("Need at least 2 numeric columns for correlation!")


    st.markdown("---")
    st.header("Step 5: Automatic Chart Generation")
    st.write("Charts automatically created based on your data!")

    st.subheader("Numeric Column Distributions")
    st.write("Shows how values are spread in each numeric column:")

    for i in range(0, len(kpi_cols), 2):
        group = kpi_cols[i:i+2]
        cols = st.columns(2)

        for j, col in enumerate(group):
            with cols[j]:
                fig, ax = plt.subplots(figsize=(6, 4))

                ax.hist(
                    df_clean[col].dropna(),
                    bins=20,
                    color='steelblue',
                    edgecolor='white',
                    alpha=0.8
                )

                ax.set_title(
                    f'Distribution of {col}',
                    fontsize=12,
                    fontweight='bold'
                )
                ax.set_xlabel(col)
                ax.set_ylabel('Count')

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                st.pyplot(fig)
                plt.close()


    st.markdown("---")
    st.subheader("Top Categories Analysis")
    st.write("Shows top values for each text column:")

    text_cols_chart = df_clean.select_dtypes(
        include=['object']
    ).columns.tolist()

    if len(text_cols_chart) > 0:

        selected_cat = st.selectbox(
            "Select a category column to analyze:",
            text_cols_chart
        )

        selected_num = st.selectbox(
            "Select a numeric column to measure by:",
            kpi_cols
        )

        chart_data = df_clean.groupby(selected_cat)[
            selected_num
        ].sum().sort_values(ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 5))

        bars = ax.bar(
            chart_data.index,
            chart_data.values,
            color='steelblue',
            edgecolor='white'
        )

        for bar, val in zip(bars, chart_data.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01 * max(chart_data.values),
                f'{val:,.0f}',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )

        ax.set_title(
            f'Top 10 {selected_cat} by {selected_num}',
            fontsize=14,
            fontweight='bold'
        )
        ax.set_xlabel(selected_cat)
        ax.set_ylabel(selected_num)
        plt.xticks(rotation=45, ha='right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()


    st.markdown("---")
    st.subheader("Trend Analysis")
    st.write("Shows how values change over time or sequence:")

    trend_col = st.selectbox(
        "Select column to see trend:",
        kpi_cols,
        key="trend_select"
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df_clean.index,
        df_clean[trend_col],
        color='steelblue',
        linewidth=1.5,
        alpha=0.8
    )

    window = min(7, len(df_clean) // 10)
    moving_avg = df_clean[trend_col].rolling(
        window=window
    ).mean()

    ax.plot(
        df_clean.index,
        moving_avg,
        color='coral',
        linewidth=2.5,
        label=f'{window}-period Moving Avg',
        linestyle='--'
    )

    ax.set_title(
        f'Trend of {trend_col}',
        fontsize=14,
        fontweight='bold'
    )
    ax.set_xlabel('Index')
    ax.set_ylabel(trend_col)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


    st.markdown("---")
    st.subheader("Category Share")
    st.write("Shows percentage share of each category:")

    if len(text_cols_chart) > 0:
        pie_data = df_clean.groupby(selected_cat)[
            selected_num
        ].sum().sort_values(ascending=False).head(6)

        fig, ax = plt.subplots(figsize=(8, 6))

        colors = [
            '#4e79a7', '#f28e2b', '#e15759',
            '#76b7b2', '#59a14f', '#edc948'
        ]

        wedges, texts, autotexts = ax.pie(
            pie_data.values,
            labels=pie_data.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=140,
            pctdistance=0.8
        )

        for autotext in autotexts:
            autotext.set_fontweight('bold')

        ax.set_title(
            f'{selected_cat} Distribution by {selected_num}',
            fontsize=14,
            fontweight='bold'
        )

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()



    st.markdown("---")
    st.subheader("Correlation Heatmap")
    st.write(
        "Shows which columns are strongly related "
        "to each other:"
    )

    if len(kpi_cols) > 1:
        corr_matrix = df_clean[kpi_cols].corr()

        fig, ax = plt.subplots(
            figsize=(8, 6)
        )

        im = ax.imshow(
            corr_matrix,
            cmap='coolwarm',
            aspect='auto',
            vmin=-1,
            vmax=1
        )

        plt.colorbar(im, ax=ax)

        ax.set_xticks(range(len(kpi_cols)))
        ax.set_yticks(range(len(kpi_cols)))
        ax.set_xticklabels(kpi_cols, rotation=45, ha='right')
        ax.set_yticklabels(kpi_cols)

        for i in range(len(kpi_cols)):
            for j in range(len(kpi_cols)):
                ax.text(
                    j, i,
                    f'{corr_matrix.iloc[i, j]:.2f}',
                    ha='center',
                    va='center',
                    fontweight='bold',
                    color='white' if abs(
                        corr_matrix.iloc[i, j]
                    ) > 0.5 else 'black'
                )

        ax.set_title(
            'Correlation Heatmap',
            fontsize=14,
            fontweight='bold'
        )

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    else:
        st.info(
            "Need at least 2 numeric columns "
            "for correlation heatmap!"
        )


    st.markdown("---")
    st.header("Step 6: Analytics Summary Report")
    st.write("Auto-generated summary of your entire dataset!")

    st.subheader("Dataset Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"""
        **Dataset Snapshot**
        - Total Rows: **{df_clean.shape[0]:,}**
        - Total Columns: **{df_clean.shape[1]}**
        - Numeric Columns: **{len(kpi_cols)}**
        - Text Columns: **{len(text_cols_chart)}**
        - Duplicate Rows Removed: **{duplicate_count}**
        - Missing Values Fixed: **{missing_count}**
        """)

    with col2:
        st.success(f"""
        **Numeric Summary**
        - Highest Column Total: **{df_clean[kpi_cols].sum().idxmax()}**
        - Lowest Column Total: **{df_clean[kpi_cols].sum().idxmin()}**
        - Most Varied Column: **{df_clean[kpi_cols].std().idxmax()}**
        - Most Stable Column: **{df_clean[kpi_cols].std().idxmin()}**
        """)

    st.markdown("---")
    st.subheader("Key Findings")

    findings = []

    for col in kpi_cols:
        total = df_clean[col].sum()
        avg = df_clean[col].mean()
        maximum = df_clean[col].max()
        minimum = df_clean[col].min()

        findings.append(
            f"• **{col}** ranges from "
            f"**{minimum:,.2f}** to **{maximum:,.2f}** "
            f"with an average of **{avg:,.2f}** "
            f"and total of **{total:,.2f}**"
        )

    for finding in findings:
        st.markdown(finding)

    if len(text_cols_chart) > 0:
        st.markdown("---")
        st.subheader("Category Findings")

        for col in text_cols_chart[:5]:
            unique_count = df_clean[col].nunique()
            most_common = df_clean[col].mode()[0]
            most_common_count = df_clean[col].value_counts().iloc[0]
            pct = (most_common_count / len(df_clean)) * 100

            st.markdown(
                f"• **{col}** has **{unique_count}** unique values. "
                f"Most common: **{most_common}** "
                f"appearing **{most_common_count}** times "
                f"(**{pct:.1f}%** of data)"
            )

    st.markdown("---")
    st.subheader("Download Your Clean Dataset")
    st.write("Download your cleaned data as a CSV file!")

    clean_csv = df_clean.to_csv(index=False)

    st.download_button(
        label="Download Clean CSV",
        data=clean_csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    st.success(
        "Analysis Complete! "
        "Your data has been fully analyzed."
    )