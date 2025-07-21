import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=== TIPOS DE VARIABLES ===")
cursor.execute('SELECT id, name, description FROM main_app_variabletype')
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Nombre: {row[1]}, Descripción: {row[2]}")

print("\n=== CONFIGURACIONES DEL SISTEMA ===")
cursor.execute('SELECT key, value, description FROM main_app_systemconfiguration')
for row in cursor.fetchall():
    print(f"Clave: {row[0]}, Valor: {row[1]}, Descripción: {row[2]}")

print(f"\n=== ESTADÍSTICAS GENERALES ===")
cursor.execute('SELECT COUNT(*) FROM main_app_variabletype')
print(f"Tipos de variables: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM main_app_systemconfiguration')
print(f"Configuraciones: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM auth_user')
print(f"Usuarios: {cursor.fetchone()[0]}")

conn.close()
print("\n✅ Base de datos SQLite3 configurada correctamente!")
