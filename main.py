import pandas as pd
food_orders = pd.read_csv("food_orders_new_delhi.csv")
print(food_orders.head())
print(food_orders.info())


# Data cleaning
# Converting "Order Date and Time” and “Delivery Date and Time" to datetime format
# Converting "Discounts and Offers" to numeric values

from datetime import datetime

#conerting date and time columns to datetime
food_orders['Order Date and Time'] = pd.to_datetime(food_orders['Order Date and Time'])
food_orders['Delivery Date and Time'] = pd.to_datetime(food_orders['Delivery Date and Time'])

# Creating function to extract numeric values from the 'Discounts and Offers' string
def extract_discount(discount_str):
    if isinstance(discount_str, str): 
        if 'off' in discount_str:
            return float(discount_str.split(' ')[0])
        elif '%' in discount_str:
            return float(discount_str.split('%')[0])
        else:
            return 0.0

#applying the above function to create a new 'Discount Percentage' column
food_orders['Discount Percentage'] = food_orders['Discounts and Offers'].apply(extract_discount)

#to calculate percentage discounts, calculate discount amount based on order value
food_orders['Discount Amount'] = food_orders.apply(lambda x: (x['Order Value'] * x['Discount Percentage'] / 100)
                                                   if x['Discount Percentage']>1
                                                   else x['Discount Percentage'], axis =1)

#adjust 'Discount Amount for fixed discounts directly specified in the 'Discounts and Offers' column
food_orders['Discount Amount'] = food_orders.apply(lambda x: x['Discount Amount'] if x['Discount Percentage']
                                                   else x['Order Value'] * x['Discount Percentage'] / 100, axis=1)

print(food_orders[['Order Value', 'Discounts and Offers','Discount Percentage', 'Discount Amount']].head(), food_orders.dtypes)

#For cost analysis we'll consider  the delivery cost, payment processing fee and discount amount
# The revenue is dervied from the Commission fee. To calculate net profit, subtract total cost(inclusing discounts) from the revenue generated through commission fees.

# #calculate total costs and revenue per order and profit
food_orders['Total Costs'] = food_orders['Delivery Fee'] + food_orders['Payment Processing Fee'] + food_orders['Discount Amount']
food_orders['Revenue'] = food_orders['Commission Fee']
food_orders['Profit'] = food_orders['Revenue'] - food_orders['Total Costs']
print("Data with Total Costs, Revenue, and Profit:", food_orders[['Total Costs', 'Revenue', 'Profit']].head())
#aggregating data to get overall results
total_orders = food_orders.shape[0]
total_revenue = food_orders['Revenue'].sum()
total_costs = food_orders['Total Costs'].sum()
total_profit = food_orders['Profit'].sum()

overall_results= {
    "Total Orders" : total_orders,
    "Total Revenue" : total_revenue,
    "Total Costs" : total_costs,
    "Total Profit" : total_profit
}
print("Overall results:",overall_results)

#plotting hostogram of profits per order to visualize the distribution of profitable and unprofitable orders
import matplotlib.pyplot as plt

#histogram for profits per order
plt.figure(figsize=(12,6))
plt.hist(food_orders['Profit'], bins=50, color='blue', edgecolor='black')
plt.title('Profit Distribution per Order in Zomato Food Delivery')
plt.xlabel('Profit')
plt.ylabel('Number of Orders')
plt.axvline(food_orders['Profit'].mean(), color='red', linestyle='dashed',linewidth=1)
plt.show()

#pie chart for proportion of costs
costs_breakdown = food_orders[['Delivery Fee', 'Payment Processing Fee','Discount Amount']].sum()
plt.figure(figsize=(8,8))
plt.pie(costs_breakdown, labels = costs_breakdown.index, autopct='%1.1f%%', startangle=320)
plt.title('Proportion of Total Costs in Zomato Food Delivery')
plt.show()

#bar chart for total revenue, costs and profit
totals = ['Total Revenue', 'Total Costs', 'Total Profit']
values= [total_revenue, total_costs, total_profit]

plt.figure(figsize=(12,6))
plt.bar(totals, values, color=['green', 'purple', 'blue'])
plt.title('Total Revenue, Costs, and Profit')
plt.ylabel('Amount (INR)')
plt.show()

# The graphs show that there is absolutely no profitability. We nned to find a sweet spot for offering discounts and charging commissions.
# We need to find a new average commission % based on profitable orders and a new avg discount % for profitable orders.
# Find avg discount % provides a guideline for what level of discount allows for profitability.

#filter the dataset for profitable orders
profitable_orders = food_orders[['Profit']]
# print(profitable_orders.columns)

#calculate avg commission % for profitable orders
# profitable_orders['Commission Percentage'] = (profitable_orders['Commission Fee'] / profitable_orders['Order Value']) * 100
# Using food_orders instead of profitable_orders here because profitable_orders is a snapshot(taken before filtering the food_order) of food_orders and doesnt contain the new columns(i.e, commission fee)
profitable_orders['Commission Percentage'] = (food_orders['Commission Fee'] / food_orders['Order Value']) * 100

#Calculate avg discount % for profitable orders
profitable_orders['Effective Discount Percentage'] = (food_orders['Discount Amount'] / food_orders['Order Value']) * 100

#calculate new avgs
new_avg_commission_percentage = profitable_orders['Commission Percentage'].mean()
new_avg_discount_percentage = profitable_orders['Effective Discount Percentage'].mean()

print(new_avg_commission_percentage, new_avg_discount_percentage)

#simulate the profitability with recommended discounts and commissions
recommended_commission_percentage = 19.75
recommended_discount_percentage = 19.95

# calculate the simulated commission fee and discount amount using recommended percentages
food_orders['Simulated Commission Fee'] = food_orders['Order Value'] * (recommended_commission_percentage / 100)
food_orders['Simulated Discount Amount'] = food_orders['Order Value'] * (recommended_discount_percentage / 100)

# recalculate total costs and profit with simulated values
food_orders['Simulated Total Costs'] = (food_orders['Delivery Fee'] +
                                        food_orders['Payment Processing Fee'] +
                                        food_orders['Simulated Discount Amount'])

food_orders['Simulated Profit'] = (food_orders['Simulated Commission Fee'] -
                                   food_orders['Simulated Total Costs'])

# visualizing the comparison
import seaborn as sns

plt.figure(figsize=(14, 7))

# actual profitability
sns.kdeplot(food_orders['Profit'], label='Actual Profitability', fill=True, alpha=0.5, linewidth=2)

# simulated profitability
sns.kdeplot(food_orders['Simulated Profit'], label='Estimated Profitability with Recommended Rates', fill=True, alpha=0.5, linewidth=2)

plt.title('Comparison of Profitability in Food Delivery: Actual vs. Recommended Discounts and Commissions')
plt.xlabel('Profit')
plt.ylabel('Density')
plt.legend(loc='upper left')
plt.show()

print(food_orders.info())