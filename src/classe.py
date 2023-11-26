class Infos:
  def __init__(self, cidade, ocorrenciax, ocorrenciay, total):
    self.cidade = cidade
    self.ocorrenciax = ocorrenciax
    self.ocorrenciay = ocorrenciay
    self.total = total
    self.latitude = 0
    self.longitude = 0
    self.cor = 'white'

  def incrementar_ocorrenciax(self, valor):
    self.ocorrenciax += valor   # Não residencial

  def incrementar_ocorrenciay(self, valor):
    self.ocorrenciay += valor   # Residencial

  def somarTotal(self):
    self.total = self.ocorrenciay + self.ocorrenciax   # Residencial

  def coordenas(self, latitude, longitude):
    self.latitude = latitude
    self.longitude = longitude