import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('ssp.notificaciones@gmail.com', 'duof qzcf uxrn pjbx')
    print("Conexión SMTP exitosa. Configuración correcta.")
    server.quit()
except Exception as e:
    print(f"Error al conectar al servidor SMTP: {e}")
