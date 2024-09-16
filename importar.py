import pandas as pd
import sqlite3, sys

def import_excel_to_sqlite(db_name, table_name, excel_filepath, sheet_name=0):
    # Leer el archivo Excel
    df = pd.read_excel(excel_filepath, sheet_name=sheet_name)

    # Eliminar filas que estén completamente vacías
    df.dropna(how='all', inplace=True)

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Crear la tabla si no existe
    columns = ', '.join([f'"{col}" TEXT' for col in df.columns])
    print(columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

    # Insertar los datos
    for _, row in df.iterrows():
        print(row)
        # Solo insertar filas que no tengan ningún valor nulo en las columnas
        if not row.isnull().any():
            placeholders = ', '.join(['?' for _ in df.columns])
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(row))

    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Revisar si se pasaron suficientes argumentos
    if len(sys.argv) < 5:
        print("Uso: python importar.py <db_name> <table_name> <excel_filepath> <sheet_name>")
    else:
        # Asignar argumentos pasados desde la línea de comandos
        db_name = sys.argv[1]
        table_name = sys.argv[2]
        excel_filepath = sys.argv[3]
        sheet_name = sys.argv[4]   # Aquí sheet_name se pasa como cadena, puedes convertirlo a int si es necesario

        # Llamar a la función con los argumentos proporcionados
        import_excel_to_sqlite(db_name, table_name, excel_filepath, sheet_name)