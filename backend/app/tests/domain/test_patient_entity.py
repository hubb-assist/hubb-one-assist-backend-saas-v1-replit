"""
Testes para a entidade Patient com Value Objects
"""
import unittest
from datetime import date
from app.domain.patient.entities import PatientEntity
from app.domain.patient.value_objects.cpf import CPF
from app.domain.patient.value_objects.phone import Phone
from app.domain.patient.value_objects.address import Address


class TestPatientEntity(unittest.TestCase):
    """
    Testes unitários para a entidade Patient com Value Objects.
    """
    
    def test_patient_creation_with_value_objects(self):
        """
        Testa a criação de um paciente com os Value Objects CPF, Phone e Address.
        """
        # Criar um paciente com dados válidos
        patient = PatientEntity(
            name="João da Silva",
            cpf="123.456.789-09",
            rg="12.345.678-9",
            birth_date=date(1980, 1, 1),
            phone="(11) 98765-4321",
            zip_code="12345-678",
            address="Rua das Flores",
            number="123",
            complement="Apto 101",
            district="Centro",
            city="São Paulo",
            state="SP"
        )
        
        # Verificar se os Value Objects foram criados corretamente
        self.assertEqual(patient.name, "João da Silva")
        self.assertEqual(patient.cpf, "123.456.789-09")
        self.assertEqual(patient.cpf_unformatted, "12345678909")
        self.assertEqual(patient.rg, "12.345.678-9")
        self.assertEqual(patient.birth_date, date(1980, 1, 1))
        self.assertEqual(patient.phone, "(11) 98765-4321")
        self.assertEqual(patient.phone_unformatted, "11987654321")
        self.assertEqual(patient.zip_code, "12345-678")
        self.assertEqual(patient.address, "Rua das Flores")
        self.assertEqual(patient.number, "123")
        self.assertEqual(patient.complement, "Apto 101")
        self.assertEqual(patient.district, "Centro")
        self.assertEqual(patient.city, "São Paulo")
        self.assertEqual(patient.state, "SP")
        self.assertTrue("Rua das Flores, 123" in patient.full_address)
        self.assertTrue("São Paulo-SP" in patient.full_address)
    
    def test_patient_creation_with_invalid_data(self):
        """
        Testa que a criação de um paciente com dados inválidos gera exceções.
        """
        # CPF inválido
        with self.assertRaises(ValueError):
            PatientEntity(
                name="João da Silva",
                cpf="111.111.111-11",  # CPF inválido (todos os dígitos iguais)
            )
        
        # Telefone inválido
        with self.assertRaises(ValueError):
            PatientEntity(
                name="João da Silva",
                cpf="123.456.789-09",
                phone="12345"  # Telefone inválido (formato incorreto)
            )
        
        # CEP inválido
        with self.assertRaises(ValueError):
            PatientEntity(
                name="João da Silva",
                cpf="123.456.789-09",
                zip_code="1234"  # CEP inválido (formato incorreto)
            )
        
        # UF inválida
        with self.assertRaises(ValueError):
            PatientEntity(
                name="João da Silva",
                cpf="123.456.789-09",
                state="XX"  # UF inválida
            )
    
    def test_patient_update_methods(self):
        """
        Testa os métodos de atualização de um paciente com Value Objects.
        """
        # Criar um paciente
        patient = PatientEntity(
            name="João da Silva",
            cpf="123.456.789-09"
        )
        
        # Atualizar informações de contato
        patient.update_contact_info(phone="11987654321")
        self.assertEqual(patient.phone, "(11) 98765-4321")
        
        # Tentar atualizar com telefone inválido
        with self.assertRaises(ValueError):
            patient.update_contact_info(phone="123")
        
        # Atualizar endereço
        patient.update_address(
            zip_code="12345678",
            address="Rua Nova",
            number="456",
            district="Novo Bairro",
            city="Rio de Janeiro",
            state="RJ"
        )
        
        self.assertEqual(patient.zip_code, "12345678")
        self.assertEqual(patient.address, "Rua Nova")
        self.assertEqual(patient.number, "456")
        self.assertEqual(patient.city, "Rio de Janeiro")
        self.assertEqual(patient.state, "RJ")
        
        # Tentar atualizar com CEP inválido
        with self.assertRaises(ValueError):
            patient.update_address(zip_code="123")
        
        # Tentar atualizar com UF inválida
        with self.assertRaises(ValueError):
            patient.update_address(state="XX")
        
        # Atualizar informações pessoais
        patient.update_personal_info(
            name="João Silva Santos",
            rg="98.765.432-1"
        )
        
        self.assertEqual(patient.name, "João Silva Santos")
        self.assertEqual(patient.rg, "98.765.432-1")
        
        # Tentar atualizar com CPF inválido
        with self.assertRaises(ValueError):
            patient.update_personal_info(cpf="111.111.111-11")


if __name__ == "__main__":
    unittest.main()