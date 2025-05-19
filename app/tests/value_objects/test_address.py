"""
Testes para o Value Object Address
"""
import unittest
from app.domain.patient.value_objects.address import Address


class TestAddressValueObject(unittest.TestCase):
    """
    Testes unitários para o Value Object Address.
    """
    
    def test_valid_address_creation(self):
        """
        Testa a criação de um endereço com dados válidos.
        """
        # Endereço completo
        address = Address(
            zip_code="12345678",
            street="Rua das Flores",
            number="123",
            complement="Apto 101",
            district="Centro",
            city="São Paulo",
            state="SP"
        )
        
        self.assertEqual(address.zip_code, "12345678")
        self.assertEqual(address.street, "Rua das Flores")
        self.assertEqual(address.number, "123")
        self.assertEqual(address.complement, "Apto 101")
        self.assertEqual(address.district, "Centro")
        self.assertEqual(address.city, "São Paulo")
        self.assertEqual(address.state, "SP")
        
        # Verifica se o endereço é considerado completo
        self.assertTrue(address.is_complete())
        
        # Verifica a formatação como string
        self.assertIn("Rua das Flores, 123", str(address))
        self.assertIn("Centro", str(address))
        self.assertIn("São Paulo-SP", str(address))
    
    def test_address_with_minimal_data(self):
        """
        Testa a criação de um endereço com apenas os dados mínimos.
        """
        # Endereço mínimo
        address = Address(
            street="Rua das Flores",
            city="São Paulo",
        )
        
        self.assertEqual(address.street, "Rua das Flores")
        self.assertIsNone(address.number)
        self.assertEqual(address.city, "São Paulo")
        
        # Verifica se o endereço não é considerado completo
        self.assertFalse(address.is_complete())
    
    def test_address_with_invalid_data(self):
        """
        Testa que dados inválidos geram exceções.
        """
        # CEP inválido
        with self.assertRaises(ValueError):
            Address(zip_code="123456", street="Rua das Flores", city="São Paulo")
        
        # UF inválida
        with self.assertRaises(ValueError):
            Address(street="Rua das Flores", city="São Paulo", state="XX")
    
    def test_address_create_method(self):
        """
        Testa o método estático create() que trata valores vazios.
        """
        # Endereço completo
        address = Address.create(
            zip_code="12345678",
            street="Rua das Flores",
            number="123",
            complement="",  # String vazia deve ser tratada como None
            district="Centro",
            city="São Paulo",
            state="SP"
        )
        
        self.assertEqual(address.zip_code, "12345678")
        self.assertEqual(address.street, "Rua das Flores")
        self.assertEqual(address.number, "123")
        self.assertIsNone(address.complement)
        self.assertEqual(address.district, "Centro")
        self.assertEqual(address.city, "São Paulo")
        self.assertEqual(address.state, "SP")
        
        # Endereço com None e strings vazias
        address = Address.create(
            zip_code=None,
            street="Rua das Flores",
            number=None,
            complement="",
            district="",
            city="São Paulo",
            state=None
        )
        
        self.assertIsNone(address.zip_code)
        self.assertEqual(address.street, "Rua das Flores")
        self.assertIsNone(address.number)
        self.assertIsNone(address.complement)
        self.assertIsNone(address.district)
        self.assertEqual(address.city, "São Paulo")
        self.assertIsNone(address.state)
    
    def test_zip_code_format(self):
        """
        Testa a formatação de CEP.
        """
        formatted = Address.format_zip_code("12345678")
        self.assertEqual(formatted, "12345-678")
        
        # CEP já formatado
        formatted = Address.format_zip_code("12345-678")
        self.assertEqual(formatted, "12345-678")
        
        # CEP inválido
        formatted = Address.format_zip_code("1234")
        self.assertEqual(formatted, "1234")  # Mantém o valor original


if __name__ == "__main__":
    unittest.main()