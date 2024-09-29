import cv2

def leer_codigo_qr():
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)

    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()

        # Detectar y decodificar el código QR
        datos, puntos, _ = detector.detectAndDecode(frame)

        # Solo proceder si se detecta un código QR (si puntos no es None)
        if puntos is not None:
            if datos:
                print(f"Código QR detectado: {datos}")
            else:
                print("QR detectado, pero no pudo ser decodificado.")
        else:
            print("No se detectó ningún QR.")

        # Mostrar el frame
        cv2.imshow('Escáner de QR', frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    leer_codigo_qr()
