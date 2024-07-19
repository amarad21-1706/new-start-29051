
import psycopg2

try:
    connection = psycopg2.connect(host="dpg-cpbpj763e1ms739a5be0-a.frankfurt-postgres.render.com", database="audit_postgres_30051", user="audit_postgres_30051_user", password="yyRiuB4zY2eiwXp7OI9rKiW4mHGI37Rw")
    print("Connection successful!")
    connection.close()
except Exception as e:
    print("Error:", e)
