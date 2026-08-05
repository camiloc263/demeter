from enum import Enum

class EtapaCorral(str, Enum):
    gestacion = "Gestación"
    paridas = "Paridas"
    engorde = "Engorde"
    finalizacion = "Finalización"
    levante = "Levante"
    inicio = "Inicio"
    preinicio = "Preinicio"