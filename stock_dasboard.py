# -*- coding: utf-8 -*-
"""Copy of stock_dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K8xctYm95NrcdkIcbuZ0FdyuS3-bBl90
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install torch=="2.3.0"
# !pip install pandas=="2.2.2"
# !pip install matplotlib=="3.8.4"
# !pip install scikit-learn=="1.4.2"

import torch
from torch import nn
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/g5XM0-gTrOquyZcBxcJAfw/StockData.csv")
df.drop(['Unnamed: 0'], axis=1, inplace = True)

df.head()

stock_data = df
# Convert the date column into a Datetime object:
stock_data['Date'] = pd.to_datetime(df.Date)
print("Information about the dataset", end = "\n")
print(stock_data.info())

print("First five elements in the dataset", end = "\n")
print(stock_data.head(5))
print("Last five elements in the dataset", end = "\n")
print(stock_data.tail(5))

stock_data = stock_data.sort_values(by="Date")
print(stock_data.head())

from sklearn.preprocessing import MinMaxScaler
price = stock_data[['High','Low','Open','Close']]
print(price[:5])

scaler = MinMaxScaler(feature_range=(-1, 1))
price = scaler.fit_transform(price.values)
print(price[:5])

train_window = 7
import numpy as np
def create_in_out_sequences(price, tw):
    inout_seq = []
    L = len(price)
    print('Length = ', L)

    for i in range(L-tw):
        data_seq = price[i:i+tw]
        data_label = price[i+tw:i+tw+1][0][3]
        inout_seq.append((data_seq ,data_label))

    data = inout_seq;
    print('size of data : ', len(data))

    test_set_size = 20
    train_set_size = len(data) - (test_set_size);
    print('size of test : ', test_set_size)
    print('size of train : ', train_set_size)

    train = data[:train_set_size]
    test = data[train_set_size:]
    train = train[:-(tw-1)]
    return train, test

train,test = create_in_out_sequences(price, train_window)

print(test[0])
print(train[-1])

class LSTM(nn.Module):
    def __init__(self, input_size=4, hidden_layer_size=100, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size

        self.lstm = nn.LSTM(input_size, hidden_layer_size)

        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
                       torch.zeros(1,1,self.hidden_layer_size),
                      )
        lstm_out, hidden_cell = self.lstm(input_seq.view(len(input_seq), 1, -1), hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]

model = LSTM()
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

from tqdm.notebook import tqdm

epochs = 5
for i in tqdm(range(epochs)):
    epoch_loss = 0
    for seq, labels in tqdm(train):
        seq = torch.from_numpy(np.array(seq)).type(torch.FloatTensor)
        labels = torch.from_numpy(np.array(labels)).type(torch.FloatTensor)

        optimizer.zero_grad()

        y_pred = model(seq)

        labels = labels.view(1)

        single_loss = loss_function(y_pred, labels)
        single_loss.backward()
        optimizer.step()

        epoch_loss += single_loss.item()

    average_loss = epoch_loss / len(train)
    print(f'epoch: {i:3} loss: {average_loss:.10f}')

model.eval()
actual = []
pred = []

for seq, labels in test:
    seq = torch.from_numpy(np.array(seq)).type(torch.FloatTensor)
    labels = torch.from_numpy(np.array(labels)).type(torch.FloatTensor)
    actual.append(labels.item())
    with torch.no_grad():
        pred.append(model(seq).item())

actual = np.array(actual)
pred = np.array(pred)

pred = torch.from_numpy(np.array(pred)).type(torch.Tensor)
actual = torch.from_numpy(np.array(actual)).type(torch.Tensor)

print(pred)
print(actual)

import numpy as np
pred_new = scaler.inverse_transform(np.c_[np.zeros(20),np.zeros(20),np.zeros(20),np.array(pred)])
print(pred_new[:,3])

actual_new = scaler.inverse_transform(np.c_[np.zeros(20),np.zeros(20),np.zeros(20),np.array(actual)])
print(actual_new[:,3])

from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(actual_new, pred_new)
print("Mean Absolute Error (MAE):", mae)

rmse = np.sqrt(mean_squared_error(actual_new, pred_new))
print("Root Mean Squared Error (RMSE):", rmse)

fig, ax = plt.subplots()

ax.plot(actual_new[:,3], 'r-', label='Actual')
ax.plot(pred_new[:,3], 'c-', label='Predicted')

ax.set_ylabel('Stock Value (dollars)')

ax.set_ylim(min(min(actual_new[:,3]), min(pred_new[:,3])) - 5, max(max(actual_new[:,3]), max(pred_new[:,3])) + 5)
plt.xticks([])

ax.legend(loc='upper left')

plt.show()

difference = actual_new - pred_new
fig = plt.figure()
diffGraph = fig.add_axes([0,0,1,1])
diffGraph.plot(difference[:, 3], 'b')
diffGraph.set_ylabel('Difference between Actual and Predicted Stock Value (dollars)')
plt.xticks([])
plt.show()

pip install dash

import dash
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

# (Your trained model import here)
# from your_project import model, scaler

# Assuming you have already defined your model, loss function, and optimizer

epochs = 5
for i in range(epochs):
    epoch_loss = 0
    for seq, labels in train:
        seq = torch.from_numpy(np.array(seq)).type(torch.FloatTensor)
        labels = torch.from_numpy(np.array(labels)).type(torch.FloatTensor)

        optimizer.zero_grad()  # Cleartorch.save(model, 'model.pth')  # Save the trained model to a file
 previous gradients

        y_pred = model(seq)  # Forward pass

        labels = labels.view(1)  # Reshape labels to match predictions

        single_loss = loss_function(y_pred, labels)  # Calculate loss
        single_loss.backward()  # Backpropagation
        optimizer.step()  # Update weights

        epoch_loss += single_loss.item()

    average_loss = epoch_loss / len(train)  # Average loss for the epoch
    print(f'epoch: {i+1:3} loss: {average_loss:.10f}')

torch.save(model, 'model.pth')  # Save the trained model to a file

model = torch.load('model.pth')  # Load the trained model

# Load the dataset (or replace it with real-time data source)
df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/g5XM0-gTrOquyZcBxcJAfw/StockData.csv")
scaler = MinMaxScaler(feature_range=(-1, 1))

# Load your trained model (ensure the model is saved in a .pt or .pkl file)
model = torch.load('model.pth')  # Use your saved model here

# Normalize data for the LSTM model
price = df[['High', 'Low', 'Open', 'Close']]
price_scaled = scaler.fit_transform(price.values)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Stock Price Prediction Dashboard'),

    dcc.Graph(
        id='prediction-graph',
        figure={}
    ),

    html.Button('Predict Next Value', id='predict-button', n_clicks=0)
])

from dash.dependencies import Input, Output

@app.callback(
    Output('prediction-graph', 'figure'),
    [Input('predict-button', 'n_clicks')]
)
def update_graph(n_clicks):
    # Make prediction for the next value using the model
    model.eval()

    actual = df['Close'].values[-20:]  # Last 20 days actual data for comparison
    pred = []  # Store predictions

    with torch.no_grad():
        for seq in price_scaled[-20:]:
            seq = torch.tensor(seq, dtype=torch.float32).unsqueeze(0)
            prediction = model(seq)
            pred.append(prediction.item())

    pred_unscaled = scaler.inverse_transform(np.array(pred).reshape(-1, 1))  # Inverse scaling

    # Create the figure for the graph
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=np.arange(len(actual)), y=actual, mode='lines', name='Actual'))
    fig.add_trace(go.Scatter(x=np.arange(len(pred_unscaled)), y=pred_unscaled.flatten(), mode='lines', name='Predicted'))

    fig.update_layout(title='Stock Price Prediction', xaxis_title='Days', yaxis_title='Price')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)


