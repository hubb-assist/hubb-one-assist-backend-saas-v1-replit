"""
Entidades de domínio para pacientes no sistema HUBB ONE Assist.
Implementa a lógica de negócio relacionada a pacientes independente da infraestrutura.
"""
from uuid import UUID, uuid4
from datetime import date, datetime
from typing import Optional

from app.domain.patient.value_objects.cpf import CPF
from app.domain.patient.value_objects.phone import Phone
from app.domain.patient.value_objects.address import Address


class PatientEntity:
    """
    Entidade rica que representa um paciente no sistema.
    Contém dados e comportamentos relacionados a pacientes.
    Utiliza Value Objects para garantir a validade dos dados essenciais.
    """
    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = "",
        cpf: str = "",
        rg: Optional[str] = None,
        birth_date: Optional[date] = None,
        phone: Optional[str] = None,
        zip_code: Optional[str] = None,
        address: Optional[str] = None,
        number: Optional[str] = None,
        complement: Optional[str] = None,
        district: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        subscriber_id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        # Identificação e dados básicos
        self.id = id or uuid4()
        self.name = name.strip()
        
        # Value Objects para validação e formatação
        self._cpf = CPF.create(cpf)
        self.rg = rg.strip() if rg else None
        self.birth_date = birth_date
        self._phone = Phone.create(phone)
        
        # Value Object para endereço completo
        self._address = Address.create(
            zip_code=zip_code,
            street=address,
            number=number,
            complement=complement,
            district=district,
            city=city,
            state=state
        )
        
        # Relacionamento e auditoria
        self.subscriber_id = subscriber_id
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @property
    def cpf(self) -> str:
        """
        Retorna o CPF formatado.
        
        Returns:
            str: CPF no formato XXX.XXX.XXX-XX ou string vazia
        """
        return str(self._cpf) if self._cpf else ""
    
    @property
    def cpf_unformatted(self) -> str:
        """
        Retorna o CPF sem formatação.
        
        Returns:
            str: CPF sem pontuação, apenas números ou string vazia
        """
        return self._cpf.unformatted() if self._cpf else ""
    
    @property
    def phone(self) -> str:
        """
        Retorna o telefone formatado.
        
        Returns:
            str: Telefone no formato adequado ou string vazia
        """
        return str(self._phone) if self._phone else ""
    
    @property
    def phone_unformatted(self) -> str:
        """
        Retorna o telefone sem formatação.
        
        Returns:
            str: Telefone sem pontuação, apenas números ou string vazia
        """
        return self._phone.unformatted() if self._phone else ""
    
    @property
    def zip_code(self) -> str:
        """
        Retorna o CEP formatado.
        
        Returns:
            str: CEP formatado ou string vazia
        """
        return self._address.zip_code if self._address and self._address.zip_code else ""
    
    @property
    def address(self) -> str:
        """
        Retorna o logradouro.
        
        Returns:
            str: Logradouro ou string vazia
        """
        return self._address.street if self._address and self._address.street else ""
    
    @property
    def number(self) -> str:
        """
        Retorna o número do endereço.
        
        Returns:
            str: Número ou string vazia
        """
        return self._address.number if self._address and self._address.number else ""
    
    @property
    def complement(self) -> str:
        """
        Retorna o complemento do endereço.
        
        Returns:
            str: Complemento ou string vazia
        """
        return self._address.complement if self._address and self._address.complement else ""
    
    @property
    def district(self) -> str:
        """
        Retorna o bairro.
        
        Returns:
            str: Bairro ou string vazia
        """
        return self._address.district if self._address and self._address.district else ""
    
    @property
    def city(self) -> str:
        """
        Retorna a cidade.
        
        Returns:
            str: Cidade ou string vazia
        """
        return self._address.city if self._address and self._address.city else ""
    
    @property
    def state(self) -> str:
        """
        Retorna o estado (UF).
        
        Returns:
            str: UF ou string vazia
        """
        return self._address.state if self._address and self._address.state else ""
    
    @property
    def full_address(self) -> str:
        """
        Retorna o endereço completo formatado.
        
        Returns:
            str: Endereço completo formatado
        """
        return str(self._address) if self._address else ""
    
    def deactivate(self) -> None:
        """
        Desativa o paciente logicamente sem remover os dados.
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """
        Reativa um paciente previamente desativado.
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_contact_info(self, phone: Optional[str] = None) -> None:
        """
        Atualiza informações de contato do paciente.
        
        Args:
            phone: Novo número de telefone
            
        Raises:
            ValueError: Se o telefone for inválido
        """
        if phone is not None:
            self._phone = Phone.create(phone)
        self.updated_at = datetime.utcnow()
    
    def update_address(
        self,
        zip_code: Optional[str] = None,
        address: Optional[str] = None, 
        number: Optional[str] = None,
        complement: Optional[str] = None,
        district: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None
    ) -> None:
        """
        Atualiza o endereço do paciente.
        
        Args:
            zip_code: Novo CEP
            address: Novo logradouro
            number: Novo número
            complement: Novo complemento
            district: Novo bairro
            city: Nova cidade
            state: Novo estado
            
        Raises:
            ValueError: Se algum dos valores for inválido
        """
        # Criar um novo objeto Address com os valores atualizados
        new_address = Address.create(
            zip_code=zip_code if zip_code is not None else self.zip_code,
            street=address if address is not None else self.address,
            number=number if number is not None else self.number,
            complement=complement if complement is not None else self.complement,
            district=district if district is not None else self.district,
            city=city if city is not None else self.city,
            state=state if state is not None else self.state
        )
        
        self._address = new_address
        self.updated_at = datetime.utcnow()
    
    def update_personal_info(
        self,
        name: Optional[str] = None,
        cpf: Optional[str] = None,
        rg: Optional[str] = None,
        birth_date: Optional[date] = None
    ) -> None:
        """
        Atualiza informações pessoais do paciente.
        
        Args:
            name: Novo nome
            cpf: Novo CPF
            rg: Novo RG
            birth_date: Nova data de nascimento
            
        Raises:
            ValueError: Se o CPF for inválido
        """
        if name is not None:
            self.name = name.strip()
        if cpf is not None:
            self._cpf = CPF.create(cpf)
        if rg is not None:
            self.rg = rg.strip()
        if birth_date is not None:
            self.birth_date = birth_date
        self.updated_at = datetime.utcnow()