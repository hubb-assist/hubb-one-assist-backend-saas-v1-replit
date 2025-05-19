"""
Value Object Address para o domínio de pacientes.

Este objeto de valor representa um endereço completo, com seus diversos
componentes e regras de validação.
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Address:
    """
    Value Object para endereço completo.
    
    Esta classe imutável representa um endereço com seus diversos componentes.
    """
    zip_code: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    def __post_init__(self):
        """
        Validação do endereço ao instanciar o objeto.
        """
        # Valida o CEP, se fornecido
        if self.zip_code and not self._is_valid_zip_code(self.zip_code):
            raise ValueError(f"CEP inválido: {self.zip_code}")
        
        # Valida a UF, se fornecida
        if self.state and not self._is_valid_state(self.state):
            raise ValueError(f"UF inválida: {self.state}")
    
    def _is_valid_zip_code(self, zip_code: str) -> bool:
        """
        Verifica se o CEP é válido.
        
        Um CEP válido deve ter 8 dígitos, com ou sem hífen.
        
        Args:
            zip_code: CEP a ser validado
            
        Returns:
            bool: True se o CEP for válido, False caso contrário
        """
        # Limpa o CEP, deixando apenas números
        zip_code_clean = re.sub(r'[^0-9]', '', zip_code)
        
        # Verifica se tem 8 dígitos
        return len(zip_code_clean) == 8
    
    def _is_valid_state(self, state: str) -> bool:
        """
        Verifica se a UF é válida.
        
        Args:
            state: UF a ser validada
            
        Returns:
            bool: True se a UF for válida, False caso contrário
        """
        valid_states = {
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        }
        
        return state.upper() in valid_states
    
    @staticmethod
    def format_zip_code(zip_code: str) -> str:
        """
        Formata um CEP como XXXXX-XXX.
        
        Args:
            zip_code: CEP em formato livre
            
        Returns:
            str: CEP formatado
        """
        # Limpa o CEP, deixando apenas números
        zip_code_clean = re.sub(r'[^0-9]', '', zip_code)
        
        if len(zip_code_clean) != 8:
            return zip_code
        
        return f"{zip_code_clean[:5]}-{zip_code_clean[5:]}"
    
    @classmethod
    def create(cls, 
               zip_code: Optional[str] = None,
               street: Optional[str] = None,
               number: Optional[str] = None,
               complement: Optional[str] = None,
               district: Optional[str] = None,
               city: Optional[str] = None,
               state: Optional[str] = None) -> 'Address':
        """
        Cria um objeto Address com tratamento para valores nulos e vazios.
        
        Args:
            zip_code: CEP
            street: Logradouro
            number: Número
            complement: Complemento
            district: Bairro
            city: Cidade
            state: UF
            
        Returns:
            Address: Objeto Address
            
        Raises:
            ValueError: Se algum valor for inválido
        """
        # Normaliza valores vazios para None
        def normalize(value: Optional[str]) -> Optional[str]:
            if value is None or value.strip() == '':
                return None
            return value.strip()
        
        return cls(
            zip_code=normalize(zip_code),
            street=normalize(street),
            number=normalize(number),
            complement=normalize(complement),
            district=normalize(district),
            city=normalize(city),
            state=normalize(state)
        )
    
    def is_complete(self) -> bool:
        """
        Verifica se o endereço está completo.
        
        Um endereço completo deve ter pelo menos CEP, logradouro, número,
        bairro, cidade e UF.
        
        Returns:
            bool: True se o endereço estiver completo, False caso contrário
        """
        required_fields = [
            self.zip_code, self.street, self.number,
            self.district, self.city, self.state
        ]
        
        return all(field is not None for field in required_fields)
    
    def __str__(self) -> str:
        """
        Retorna o endereço formatado.
        
        Returns:
            str: Endereço formatado
        """
        parts = []
        
        if self.street:
            parts.append(self.street)
            
            if self.number:
                parts[-1] += f", {self.number}"
        
        if self.complement:
            parts.append(self.complement)
        
        if self.district:
            parts.append(self.district)
        
        if self.city and self.state:
            parts.append(f"{self.city}-{self.state}")
        elif self.city:
            parts.append(self.city)
        elif self.state:
            parts.append(self.state)
        
        if self.zip_code:
            parts.append(self.format_zip_code(self.zip_code))
        
        return ", ".join(parts)