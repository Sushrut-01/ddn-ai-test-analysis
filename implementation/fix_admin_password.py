"""Fix admin user password in Docker PostgreSQL"""
import psycopg2
import bcrypt

# Connect to Docker PostgreSQL
conn = psycopg2.connect(
    host='127.0.0.1',
    port=5434,
    database='ddn_ai_analysis',
    user='postgres',
    password='password'
)

# Generate fresh hash
password = "admin123"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Generated hash: {password_hash}")

# Update user
cur = conn.cursor()
cur.execute(
    "UPDATE users SET password_hash = %s WHERE email = %s RETURNING id, email, password_hash;",
    (password_hash, 'admin@example.com')
)

result = cur.fetchone()
if result:
    print(f"\nUpdated user ID {result[0]}: {result[1]}")
    print(f"Password hash in DB: {result[2]}")
else:
    print("\nNo user updated")

conn.commit()
cur.close()
conn.close()

print("\n[OK] Password updated successfully")
