from abc import ABC, abstractmethod

class AbstractSourceAdmin(ABC):
    """
        Classe que abstrai um administrador de fontes de conteúdo para criação de flash cards."""
    @abstractmethod
    def return_sources(self) -> None:
        """
            Assinatura para estabelecer o contrato de implementação desse método que deverá retornar as fontes."""
        ...

    @abstractmethod
    def update_sources(self) -> None:
        """
            Assinatura para estabelecer o contrato de implementação desse método que deverá atualizar as fontes."""
        ...


class AbstractCardWriter(ABC):
    """
        Abstração de um escritor de flash cards."""
    @abstractmethod
    def get_phrases(self) -> None:
        """
            Assinatura de um contrato que implementa a obtenção de frases pelas classes posteriores."""
        ...

    @abstractmethod
    def write(self) -> None:
        """
            Assinatura de um contrato que implementa a escrita de frases em objetos MyCard pelas classes posteriores."""
        ...



class AbstractCardDeliverer(ABC):
    
    def __init__(self):
        self._card_list = []

    @property
    def card_list(self):
        return self._card_list.copy()

    @abstractmethod
    def deliver(self):
        ...
    
    @abstractmethod
    def _insert_card(self):
        ...

    @abstractmethod
    def _update_card(self):
        ...
