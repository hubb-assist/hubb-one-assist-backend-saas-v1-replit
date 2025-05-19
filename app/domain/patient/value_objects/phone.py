"""
Value Object Phone para o domínio de pacientes.

Este objeto de valor representa um telefone válido, com regras 
de validação e formatação.
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Phone:
    """
    Value Object para telefone.
    
    Esta classe imutável representa um número de telefone com validação e formatação.
    """
    value: str
    
    def __post_init__(self):
        """
        Validação do telefone ao instanciar o objeto.
        Garante que apenas telefones válidos sejam criados.
        """
        if not self._is_valid():
            raise ValueError(f"Telefone inválido: {self.value}")
    
    def _is_valid(self) -> bool:
        """
        Verifica se o telefone é válido.
        
        Um telefone válido deve ter entre 10 e 11 dígitos (com DDD).
        
        Returns:
            bool: True se o telefone for válido, False caso contrário.
        """
        # Limpa o telefone, deixando apenas números
        phone = re.sub(r'[^0-9]', '', self.value)
        
        # Verifica se tem entre 10 e 11 dígitos
        if len(phone) < 10 or len(phone) > 11:
            return False
        
        # Se tiver 11 dígitos, o primeiro dígito após o DDD deve ser 9 (celular)
        if len(phone) == 11 and phone[2] != '9':
            return False
        
        # DDD deve estar entre 11 e 99
        ddd = int(phone[:2])
        if ddd < 11 or ddd > 99:
            return False
        
        return True
    
    @staticmethod
    def format(value: str) -> str:
        """
        Formata um telefone como (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.
        
        Args:
            value: Telefone em formato livre
            
        Returns:
            str: Telefone formatado
        """
        # Limpa o telefone, deixando apenas números
        phone = re.sub(r'[^0-9]', '', value)
        
        if len(phone) == 11:  # Celular com 9 dígitos
            return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
        elif len(phone) == 10:  # Telefone fixo
            return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        else:
            return value
    
    @staticmethod
    def create(value: Optional[str]) -> Optional['Phone']:
        """
        Cria um objeto Phone a partir de uma string, com tratamento para valores nulos.
        
        Args:
            value: String contendo um telefone ou None
            
        Returns:
            Optional[Phone]: Objeto Phone ou None
            
        Raises:
            ValueError: Se o telefone for inválido
        """
        if value is None or value.strip() == '':
            return None
        
        return Phone(value)
    
    def __str__(self) -> str:
        """
        Retorna o telefone formatado.
        
        Returns:
            str: Telefone no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        """
        return self.format(self.value)
    
    def unformatted(self) -> str:
        """
        Retorna o telefone sem formatação.
        
        Returns:
            str: Telefone sem pontuação, apenas números
        """
        return re.sub(r'[^0-9]', '', self.value)