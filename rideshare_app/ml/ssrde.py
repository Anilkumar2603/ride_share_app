import pandas as pd
import random
from faker import Faker

# Initialize Faker for generating fake data
faker = Faker()

# Generate a synthetic dataset
data = {
    'ride_id': [i for i in range(1, 101)],
    'destination': [faker.city() for _ in range(100)],
    'date': [faker.date_this_year() for _ in range(100)],
    'time': [faker.time() for _ in range(100)],
    'driver_rating': [round(random.uniform(3.0, 5.0), 2) for _ in range(100)],
    'seats_available': [random.randint(1, 4) for _ in range(100)],
    'car_type': [random.choice(['Sedan', 'SUV', 'Hatchback', 'Van']) for _ in range(100)],
    'driver_name': [faker.name() for _ in range(100)],
}

# Convert the data into a DataFrame
ride_data = pd.DataFrame(data)

# Save the dataset to a CSV file
ride_data.to_csv('ride_data.csv', index=False)

print("Synthetic dataset created and saved as 'ride_data.csv'")
