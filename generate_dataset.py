import csv
import random
from datetime import datetime, timedelta
import os

def generate_dataset(filename, num_rows):
    start_date = datetime(2022, 1, 1)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'price', 'quantity_sold', 'demand', 'day_of_week', 'promotion_flag'])
        
        for i in range(num_rows):
            current_date = start_date + timedelta(days=i // 50) # Multiple products/transactions per day
            day_of_week = current_date.strftime('%A')
            
            # 20% chance of promotion
            promotion_flag = 1 if random.random() < 0.2 else 0
            
            base_price = round(random.uniform(2.5, 5.5), 2)
            if promotion_flag:
                price = round(base_price * 0.8, 2)
            else:
                price = base_price
                
            # simulate demand: weekends and promos have higher demand
            demand_multiplier = 1.0
            if day_of_week in ['Saturday', 'Sunday']:
                demand_multiplier *= 1.3
            if promotion_flag:
                demand_multiplier *= 1.5
                
            demand = int(random.gauss(100 * demand_multiplier, 20))
            demand = max(5, demand) # ensure minimum demand
            
            quantity_sold = int(demand * random.uniform(0.85, 1.0)) # actual sold is usually slightly less or equal to demand due to stockouts
            
            writer.writerow([current_date.strftime('%Y-%m-%d'), price, quantity_sold, demand, day_of_week, promotion_flag])

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    file_path = os.path.join('data', 'sales_history.csv')
    generate_dataset(file_path, 50000)
    print(f"Dataset generated successfully at {file_path}")
