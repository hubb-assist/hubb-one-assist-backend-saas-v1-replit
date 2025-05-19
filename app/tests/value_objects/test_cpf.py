"""
Testes para o Value Object CPF
"""
import unittest
from app.domain.patient.value_objects.cpf import CPF


class TestCPFValueObject(unittest.TestCase):
    """
    Testes unitários para o Value Object CPF.
    """
    
    def test_valid_cpf_creation(self):
        """
        Testa a criação de um CPF com dados válidos.
        """
        # CPF válido sem formatação
        cpf = CPF("12345678909")
        self.assertEqual(str(cpf), "123.456.789-09")
        self.assertEqual(cpf.unformatted(), "12345678909")
        
        # CPF válido já formatado
        cpf = CPF("123.456.789-09")
        self.assertEqual(str(cpf), "123.456.789-09")
        self.assertEqual(cpf.unformatted(), "12345678909")
    
    def test_invalid_cpf_creation(self):
        """
        Testa que CPFs inválidos geram exceções.
        """
        # CPF com tamanho incorreto
        with self.assertRaises(ValueError):
            CPF("1234567890")  # Somente 10 dígitos
        
        # CPF com todos os dígitos iguais (caso específico inválido)
        with self.assertRaises(ValueError):
            CPF("11111111111")
        
        # CPF com dígitos verificadores inválidos
        with self.assertRaises(ValueError):
            CPF("12345678900")  # Dígitos verificadores incorretos
    
    def test_cpf_create_method(self):
        """
        Testa o método estático create() que aceita valores nulos.
        """
        # CPF válido
        cpf = CPF.create("123.456.789-09")
        self.assertIsNotNone(cpf)
        self.assertEqual(str(cpf), "123.456.789-09")
        
        # Valor nulo
        cpf = CPF.create(None)
        self.assertIsNone(cpf)
        
        # String vazia
        cpf = CPF.create("")
        self.assertIsNone(cpf)
        
        # String com espaços
        cpf = CPF.create("  ")
        self.assertIsNone(cpf)
    
    def test_cpf_format_method(self):
        """
        Testa o método estático format().
        """
        # CPF sem formatação
        formatted = CPF.format("12345678909")
        self.assertEqual(formatted, "123.456.789-09")
        
        # CPF já formatado
        formatted = CPF.format("123.456.789-09")
        self.assertEqual(formatted, "123.456.789-09")
        
        # CPF inválido (tamanho incorreto)
        formatted = CPF.format("123456")
        self.assertEqual(formatted, "123456")  # Mantém o valor original


if __name__ == "__main__":
    unittest.main()