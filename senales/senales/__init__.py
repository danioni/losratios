"""Marco de señales para el rebalanceo entre TQQQ, BTC y stablecoins/USD.

Cada capa de señal vive en su propio módulo y escribe en data/series/:

- S2.x  liquidez_neta.py  (implementado)
- S3.x  flujos a ETFs     (pendiente)
- S4.x  decaimiento de TQQQ (pendiente)

Lo compartido está en nucleo.py; lo que decide un número publicado, en
configuracion.py.
"""
