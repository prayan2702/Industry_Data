import streamlit as st
import pandas as pd
import yfinance as yf
from io import BytesIO
import time

# Streamlit app title
st.title("Industry Data Downloader")
st.write("Fetch industry data for Indices and download it as an Excel file.")

# Universe selection
universe = ['Nifty50', 'Nifty100', 'Nifty200', 'Nifty250', 'Nifty500', 'N750', 'AllNSE']
U = st.selectbox('Select Universe:', universe, index=6)  # Default is 'AllNSE'

# File path selection based on universe
if U == 'N750':
    file_path = 'https://raw.githubusercontent.com/prayan2702/Industry_Data/refs/heads/main/ind_niftytotalmarket_list.csv'
elif U == 'AllNSE':
    file_path = f'https://raw.githubusercontent.com/prayan2702/Industry_Data/refs/heads/main/NSE_EQ_ALL.csv'
else:
    file_path = f'https://raw.githubusercontent.com/prayan2702/Industry_Data/refs/heads/main/ind_{U.lower()}list.csv'

# Load stock data
@st.cache_data(ttl=0)
def load_stock_data(file_path):
    df = pd.read_csv(file_path)
    df['Yahoo_Symbol'] = df.Symbol + '.NS'
    return df

st.write("Fetching stock list...")
try:
    stock_data = load_stock_data(file_path)
    st.success("Stock list fetched successfully!")
    st.write(f"Number of stocks in the universe: {len(stock_data)}")
except Exception as e:
    st.error(f"Failed to fetch stock list: {e}")

# Fetch industry data
def fetch_industry_data(symbols):
    industry_data = []
    total_symbols = len(symbols)
    chunk_size = 50  # Process in chunks of 50
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Process in chunks
    for start_idx in range(0, total_symbols, chunk_size):
        end_idx = min(start_idx + chunk_size, total_symbols)
        chunk = symbols[start_idx:end_idx]

        for idx, symbol in enumerate(chunk):
            try:
                ticker = yf.Ticker(symbol)
                company_name = ticker.info.get("longName", "N/A")
                industry = ticker.info.get("industry", "N/A")
                industry_data.append({"Company Name": company_name, "Symbol": symbol, "Industry": industry})
            except Exception as e:
                industry_data.append({"Company Name": "Error", "Symbol": symbol, "Industry": str(e)})
            
            # Update progress bar and text for current chunk
            progress = (start_idx + idx + 1) / total_symbols
            progress_bar.progress(progress)
            progress_text.text(f"Progress: {int(progress * 100)}%")
            
            # Add a short delay between requests
            time.sleep(0.5)  # Adjust this time as necessary

    return pd.DataFrame(industry_data)

# Start button to process data
if st.button("Fetch Industry Data"):
    st.write("Fetching industry data. This may take some time...")
    yahoo_symbols = stock_data['Yahoo_Symbol'].tolist()

    # Fetch industry data
    industry_df = fetch_industry_data(yahoo_symbols)

    # Display results
    st.write("Fetched Industry Data:")
    st.dataframe(industry_df)

    # Download button for Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        industry_df.to_excel(writer, index=False, sheet_name="Industry Data")
    st.download_button(
        label="Download Industry Data as Excel",
        data=output.getvalue(),
        file_name=f"{U}_Industry_Data.xlsx",  # File name based on universe
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
