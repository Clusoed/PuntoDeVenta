"""
Utilidades para conversión de monedas USD/Bs
"""
from typing import Tuple


class CurrencyConverter:
    """Clase para manejar conversiones de moneda USD <-> Bs."""
    
    def __init__(self, tasa_cambio: float = 1.0):
        self._tasa = tasa_cambio
    
    @property
    def tasa(self) -> float:
        """Obtiene la tasa de cambio actual."""
        return self._tasa
    
    @tasa.setter
    def tasa(self, nueva_tasa: float):
        """Establece una nueva tasa de cambio."""
        if nueva_tasa > 0:
            self._tasa = nueva_tasa
    
    def usd_a_bs(self, monto_usd: float) -> float:
        """Convierte dólares a bolívares."""
        return round(monto_usd * self._tasa, 2)
    
    def bs_a_usd(self, monto_bs: float) -> float:
        """Convierte bolívares a dólares."""
        if self._tasa == 0:
            return 0
        return round(monto_bs / self._tasa, 2)
    
    def formato_usd(self, monto: float) -> str:
        """Formatea un monto en dólares."""
        return f"$ {monto:,.2f}"
    
    def formato_bs(self, monto: float) -> str:
        """Formatea un monto en bolívares."""
        return f"Bs {monto:,.2f}"
    
    def formato_dual(self, monto_usd: float) -> Tuple[str, str]:
        """Retorna el monto formateado en ambas monedas."""
        monto_bs = self.usd_a_bs(monto_usd)
        return self.formato_usd(monto_usd), self.formato_bs(monto_bs)
    
    def precio_completo(self, precio_usd: float) -> dict:
        """Retorna un diccionario con el precio en ambas monedas."""
        return {
            'usd': precio_usd,
            'bs': self.usd_a_bs(precio_usd),
            'usd_fmt': self.formato_usd(precio_usd),
            'bs_fmt': self.formato_bs(self.usd_a_bs(precio_usd))
        }


# Instancia global del convertidor
_converter = CurrencyConverter()


def set_tasa_global(tasa: float):
    """Establece la tasa de cambio global."""
    _converter.tasa = tasa


def get_tasa_global() -> float:
    """Obtiene la tasa de cambio global."""
    return _converter.tasa


def usd_a_bs(monto_usd: float) -> float:
    """Convierte dólares a bolívares usando la tasa global."""
    return _converter.usd_a_bs(monto_usd)


def bs_a_usd(monto_bs: float) -> float:
    """Convierte bolívares a dólares usando la tasa global."""
    return _converter.bs_a_usd(monto_bs)


def formato_usd(monto: float) -> str:
    """Formatea un monto en dólares."""
    return _converter.formato_usd(monto)


def formato_bs(monto: float) -> str:
    """Formatea un monto en bolívares."""
    return _converter.formato_bs(monto)


def formato_dual(monto_usd: float) -> Tuple[str, str]:
    """Retorna el monto formateado en USD y Bs."""
    return _converter.formato_dual(monto_usd)
