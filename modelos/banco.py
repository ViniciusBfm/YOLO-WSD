import sqlite3

# Conecte-se ao banco de dados (substitua com o caminho correto)
conn = sqlite3.connect('../controle.db')
cursor = conn.cursor()

# Execute uma consulta para recuperar os registros da tabela
cursor.execute('SELECT * FROM capturas_cam1')
registros = cursor.fetchall()

# Exiba os registros
for registro in registros:
    print(f"ID: {registro[0]}, Timestamp: {registro[1]}, msg: {registro[2]}")



# Feche a conexão com o banco de dados
conn.close()
