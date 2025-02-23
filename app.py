import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import streamlit as st

# Load the OHLCV dataset (same data you already have)
# Load the OHLCV dataset
csv_data = 'data.csv'
df = pd.read_csv(csv_data)
df['datetime'] = pd.to_datetime(df['datetime'])

# Initialize session state for trade count if it doesn't exist
if 'trade_count' not in st.session_state:
    st.session_state.trade_count = 0

# Function to calculate EMA
def calculate_ema(data, span=9):
    return data['Close'].ewm(span=span, adjust=False).mean()

# Function to calculate MACD
def calculate_macd(data):
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = short_ema - long_ema
    data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

# Function to save trade details to CSV
def save_trade_to_csv(buy_time, buy_price, sell_time, sell_price, profit, filename="trades.csv"):
    trade_data = {
        'Buy Time': [buy_time],
        'Buy Price': [buy_price],
        'Sell Time': [sell_time],
        'Sell Price': [sell_price],
        'Profit': [profit]
    }
    trade_df = pd.DataFrame(trade_data)

    # If file doesn't exist, create it, otherwise append to it
    try:
        # Try to open the file to check if it exists
        existing_df = pd.read_csv(filename)
        # Append the new trade to the existing data
        existing_df = pd.concat([existing_df, trade_df], ignore_index=True)
        existing_df.to_csv(filename, index=False)
    except FileNotFoundError:
        # If the file doesn't exist, create a new one
        trade_df.to_csv(filename, index=False)

# Add indicators
df['EMA_9'] = calculate_ema(df, span=9)
calculate_macd(df)

# Function to check trend (bullish if price > EMA)
def check_trend(data):
    return ["Bullish" if close > ema else "Bearish" for close, ema in zip(data['Close'], data['EMA_9'])]

df["Trend"] = check_trend(df)

# Streamlit UI
st.title("📈 Interactive Crypto Trading Simulator")

# Create subplots (candlestick chart in the first row, volume chart in the second row)
fig = sp.make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.1, 
    row_heights=[0.7, 0.3],  # Make the first subplot taller for the candlestick
    subplot_titles=('Candlestick Chart', 'Volume')
)

# Create Candlestick plot (subplot 1)
fig.add_trace(go.Candlestick(
    x=df['datetime'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="OHLC"
), row=1, col=1)

# # Add EMA line to the first subplot (candlestick chart)
fig.add_trace(go.Scatter(
    x=df['datetime'],
    y=df['EMA_9'],
    mode='lines',
    name='EMA 9',
    line=dict(color='blue', width=1.5)
), row=1, col=1)

# # Add MACD line to the first subplot (candlestick chart)
# fig.add_trace(go.Scatter(
#     x=df['datetime'],
#     y=df['MACD'],
#     mode='lines',
#     name='MACD',
#     line=dict(color='purple', width=1.5)
# ), row=1, col=1)

# # Add Signal line to the first subplot (candlestick chart)
# fig.add_trace(go.Scatter(
#     x=df['datetime'],
#     y=df['Signal Line'],
#     mode='lines',
#     name='Signal Line',
#     line=dict(color='red', width=1.5)
# ), row=1, col=1)

# Create volume plot (subplot 2) in the second row
fig.add_trace(go.Bar(
    x=df['datetime'],
    y=df['Volume'],
    name="Volume",
    marker=dict(color='rgba(0, 255, 0, 0.3)')  # Light green color for volume bars
), row=2, col=1)

# Update layout
fig.update_layout(
    title="Candlestick Chart with Volume",
    xaxis_title="Time",
    yaxis_title="Price",
    height=800,  # Adjust height for better spacing
    showlegend=True
)

# Get user input for Buy/Sell
st.sidebar.header("💰 Trade Input")
buy_index = st.sidebar.selectbox("Select Buy Time", df['datetime'])
sell_index = st.sidebar.selectbox("Select Sell Time", df['datetime'])

buy_price = df.loc[df['datetime'] == buy_index, "Close"].values[0]
sell_price = df.loc[df['datetime'] == sell_index, "Close"].values[0]
profit = round(sell_price - buy_price, 2)

# Plot Buy/Sell points on the chart
fig.add_trace(go.Scatter(
    x=[buy_index],
    y=[buy_price],
    mode='markers+text',
    text="Buy ✅",
    name = 'Buy',
    marker=dict(color="green", size=10)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=[sell_index],
    y=[sell_price],
    mode='markers+text',
    text="Sell ❌",
    name = 'Sell',
    marker=dict(color="red", size=10)
), row=1, col=1)

# Show the chart in Streamlit
st.plotly_chart(fig)

# Save trade details to CSV (as implemented earlier)
# save_trade_to_csv(buy_index, buy_price, sell_index, sell_price, profit)
# Ask for confirmation before saving the trade to CSV
def clear_text():
    if  st.session_state.save_confirm.strip().lower() == "okay":
        save_trade_to_csv(buy_index, buy_price, sell_index, sell_price, profit)
        st.session_state.trade_count += 1  # Increment the trade count
        # st.sidebar.write(f"✅ **Trade details saved successfully !**")
        # st.sidebar.write(f"🔹 **Total Trades Saved:** {st.session_state.trade_count}")
        # st.session_state.save_confirm = "" 
        # Display result below input field
        st.session_state.success_message = f"✅ **Trade details saved successfully!**"
        st.session_state.trade_count_message = f"🔹 **Total Trades Saved:** {st.session_state.trade_count}"
        st.session_state.save_confirm = ""  # Clear the text input
# Initialize session state if not already initialized
if "trade_count" not in st.session_state:
    st.session_state.trade_count = 0
if "success_message" not in st.session_state:
    st.session_state.success_message = ""
if "trade_count_message" not in st.session_state:
    st.session_state.trade_count_message = ""

save_confirm = st.text_input("Type 'okay' to save the trade data to CSV:", on_change=clear_text, key="save_confirm")
# Display success message and trade count below the input field
if st.session_state.success_message:
    st.write(st.session_state.success_message)
    st.write(st.session_state.trade_count_message)


# If user types 'okay', save the trade data to CSV

    # st.session_state.save_confirm = st.session_state.widget
    # st.session_state.widget = ""


# Show trade details in the sidebar
st.sidebar.write(f"🔹 **Buy Price:** ${buy_price}")
st.sidebar.write(f"🔹 **Sell Price:** ${sell_price}")
st.sidebar.write(f"🔹 **Profit/Loss:** ${profit}")
