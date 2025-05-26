"""
Testes para o Value Object Phone
"""
import unittest
from app.domain.patient.value_objects.phone import Phone


class TestPhoneValueObject(unittest.TestCase):
    """
    Testes unitários para o Value Object Phone.
    """
    
    def test_valid_phone_creation(self):
        """
        Testa a criação de um telefone com dados válidos.
        """
        # Telefone celular válido sem formatação
        phone = Phone("11987654321")
        self.assertEqual(str(phone), "(11) 98765-4321")
        self.assertEqual(phone.unformatted(), "11987654321")
        
        # Telefone fixo válido sem formatação
        phone = Phone("1123456789")
        self.assertEqual(str(phone), "(11) 2345-6789")
        self.assertEqual(phone.unformatted(), "1123456789")
        
        # Telefone celular válido já formatado
        phone = Phone("(11) 98765-4321")
        self.assertEqual(str(phone), "(11) 98765-4321")
        self.assertEqual(phone.unformatted(), "11987654321")
        
        # Telefone fixo válido já formatado
        phone = Phone("(11) 2345-6789")
        self.assertEqual(str(phone), "(11) 2345-6789")
        self.assertEqual(phone.unformatted(), "1123456789")
    
    def test_invalid_phone_creation(self):
        """
        Testa que telefones inválidos geram exceções.
        """
        # Telefone com tamanho incorreto (menos dígitos)
        with self.assertRaises(ValueError):
            Phone("123456789")  # Somente 9 dígitos
        
        # Telefone com tamanho incorreto (mais dígitos)
        with self.assertRaises(ValueError):
            Phone("123456789012")  # 12 dígitos
        
        # Telefone com DDD inválido
        with self.assertRaises(ValueError):
            Phone("0123456789")  # DDD iniciando com 0
        
        # Celular com dígito inválido após DDD
        with self.assertRaises(ValueError):
            Phone("11887654321")  # Deveria ser 9 após o DDD para celular
    
    def test_phone_create_method(self):
        """
        Testa o método estático create() que aceita valores nulos.
        """
        # Telefone válido
        phone = Phone.create("11987654321")
        self.assertIsNotNone(phone)
        self.assertEqual(str(phone), "(11) 98765-4321")
        
        # Valor nulo
        phone = Phone.create(None)
        self.assertIsNone(phone)
        
        # String vazia
        phone = Phone.create("")
        self.assertIsNone(phone)
        
        # String com espaços
        phone = Phone.create("  ")
        self.assertIsNone(phone)
    
    def test_phone_format_method(self):
        """
        Testa o método estático format().
        """
        # Telefone celular sem formatação
        formatted = Phone.format("11987654321")
        self.assertEqual(formatted, "(11) 98765-4321")
        
        # Telefone fixo sem formatação
        formatted = Phone.format("1123456789")
        self.assertEqual(formatted, "(11) 2345-6789")
        
        # Telefone já formatado
        formatted = Phone.format("(11) 98765-4321")
        self.assertEqual(formatted, "(11) 98765-4321")
        
        # Telefone inválido (tamanho incorreto)
        formatted = Phone.format("123456")
        self.assertEqual(formatted, "123456")  # Mantém o valor original


if __name__ == "__main__":
    unittest.main()