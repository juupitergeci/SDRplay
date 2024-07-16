import SoapySDR
from SoapySDR import *  # Importar todas las funciones y clases
import numpy as np
from tqdm import tqdm

def configurar_dispositivo(freq_central, sample_rate, ancho_banda):
    args = dict(driver="sdrplay")
    sdr = SoapySDR.Device(args)
    sdr.setFrequency(SOAPY_SDR_RX, 0, freq_central)
    sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
    sdr.setBandwidth(SOAPY_SDR_RX, 0, ancho_banda)
    return sdr

def tomar_muestras(sdr, tiempo, ruta_guardado):
    rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(rx_stream)
    muestras = []
    tiempo_transcurrido = 0
    sample_rate = sdr.getSampleRate(SOAPY_SDR_RX, 0)
    total_samples = int(tiempo * sample_rate)
    buffer_size = 1024
    i=1
    with tqdm(total=total_samples, desc=f"Grabando datos ", unit=" muestras") as pbar:
        while tiempo_transcurrido < tiempo:
            buffer = np.zeros(buffer_size, np.complex64)
            sr = sdr.readStream(rx_stream, [buffer], len(buffer))
    
            if sr.ret > 0:
                muestras.extend(buffer[:sr.ret])
                tiempo_transcurrido += sr.ret / sample_rate
                pbar.update(sr.ret)

    sdr.deactivateStream(rx_stream)
    with open(ruta_guardado, "wb") as f:
        f.write(np.array(muestras).tobytes())

# Configurar frecuencia central, sample rate y ancho de banda
freq_central = 20.2e6  # Frecuencia central en Hz
sample_rate = 1e6     # Sample rate en Hz
ancho_banda = 1.536e6   # Ancho de banda en Hz
tiempo_integracion = 10  # Tiempo de integración en segundos
numero_de_segmentos = 100 # Número de segmentos de 10 segundos

if __name__ == "__main__":
    dispositivo = configurar_dispositivo(freq_central, sample_rate, ancho_banda)
    for i in range(numero_de_segmentos):
        ruta_guardado = f"/datos/muestras_{i}.bin"
        tomar_muestras(dispositivo, tiempo=tiempo_integracion, ruta_guardado=ruta_guardado)


