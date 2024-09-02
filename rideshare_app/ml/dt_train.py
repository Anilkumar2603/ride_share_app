from werkzeug.security import generate_password_hash

# Password to hash
password = 'qwerty'

# Generate hashed password
hashed_password = generate_password_hash(password)

# Generate SQL statement
sql_statement = f"""
INSERT INTO Users (user_id, username, password_hash, role, email, created_at, updated_at)
VALUES ('0001', 'Anil_kumar', '{hashed_password}', 'admin', 'anilkuma@gmail.com', NOW(), NOW());
"""

print(sql_statement)  # Print the SQL statement to execute
