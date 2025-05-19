"""
Entidades de domínio para pacientes no sistema HUBB ONE Assist.
Implementa a lógica de negócio relacionada a pacientes independente da infraestrutura.
"""
from uuid import UUID, uuid4
from datetime import date, datetime
from typing import Optional


class PatientEntity:
    """
    Entidade rica que representa um paciente no sistema.
    Contém dados e comportamentos relacionados a pacientes.
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
        self.id = id or uuid4()
        self.name = name.strip()
        self.cpf = cpf.strip()
        self.rg = rg.strip() if rg else None
        self.birth_date = birth_date
        self.phone = phone.strip() if phone else None
        
        # Endereço
        self.zip_code = zip_code.strip() if zip_code else None
        self.address = address.strip() if address else None
        self.number = number.strip() if number else None
        self.complement = complement.strip() if complement else None
        self.district = district.strip() if district else None
        self.city = city.strip() if city else None
        self.state = state.strip() if state else None
        
        # Relacionamento e auditoria
        self.subscriber_id = subscriber_id
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
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
        """
        if phone is not None:
            self.phone = phone.strip()
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
            address: Novo endereço
            number: Novo número
            complement: Novo complemento
            district: Novo bairro
            city: Nova cidade
            state: Novo estado
        """
        if zip_code is not None:
            self.zip_code = zip_code.strip()
        if address is not None:
            self.address = address.strip()
        if number is not None:
            self.number = number.strip()
        if complement is not None:
            self.complement = complement.strip()
        if district is not None:
            self.district = district.strip()
        if city is not None:
            self.city = city.strip()
        if state is not None:
            self.state = state.strip()
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
        """
        if name is not None:
            self.name = name.strip()
        if cpf is not None:
            self.cpf = cpf.strip()
        if rg is not None:
            self.rg = rg.strip()
        if birth_date is not None:
            self.birth_date = birth_date
        self.updated_at = datetime.utcnow()