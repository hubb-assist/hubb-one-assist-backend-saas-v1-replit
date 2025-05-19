"""
Value Object CPF para o domínio de pacientes.

Este objeto de valor representa um CPF válido no Brasil, com regras 
de validação e formatação.
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CPF:
    """
    Value Object para CPF.
    
    Esta classe imutável representa um CPF com validação e formatação.
    """
    value: str
    
    def __post_init__(self):
        """
        Validação do CPF ao instanciar o objeto.
        Garante que apenas CPFs válidos sejam criados.
        """
        if not self._is_valid():
            raise ValueError(f"CPF inválido: {self.value}")
    
    def _is_valid(self) -> bool:
        """
        Verifica se o CPF é válido.
        
        Returns:
            bool: True se o CPF for válido, False caso contrário.
        """
        # Limpa o CPF, deixando apenas números
        cpf = re.sub(r'[^0-9]', '', self.value)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            return False
        
        # Cálculo do primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Verifica o primeiro dígito verificador
        if digito1 != int(cpf[9]):
            return False
        
        # Cálculo do segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica o segundo dígito verificador
        return digito2 == int(cpf[10])
    
    @staticmethod
    def format(value: str) -> str:
        """
        Formata um CPF como XXX.XXX.XXX-XX.
        
        Args:
            value: CPF em formato livre
            
        Returns:
            str: CPF formatado
        """
        # Limpa o CPF, deixando apenas números
        cpf = re.sub(r'[^0-9]', '', value)
        
        if len(cpf) != 11:
            return value
        
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    @staticmethod
    def create(value: Optional[str]) -> Optional['CPF']:
        """
        Cria um objeto CPF a partir de uma string, com tratamento para valores nulos.
        
        Args:
            value: String contendo um CPF ou None
            
        Returns:
            Optional[CPF]: Objeto CPF ou None
            
        Raises:
            ValueError: Se o CPF for inválido
        """
        if value is None or value.strip() == '':
            return None
        
        return CPF(value)
    
    def __str__(self) -> str:
        """
        Retorna o CPF formatado.
        
        Returns:
            str: CPF no formato XXX.XXX.XXX-XX
        """
        return self.format(self.value)
    
    def unformatted(self) -> str:
        """
        Retorna o CPF sem formatação.
        
        Returns:
            str: CPF sem pontuação, apenas números
        """
        return re.sub(r'[^0-9]', '', self.value)