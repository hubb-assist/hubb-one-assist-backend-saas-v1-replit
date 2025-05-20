"""
Exceções comuns usadas no sistema.
"""


class EntityNotFoundException(Exception):
    """
    Exceção lançada quando uma entidade não é encontrada.
    """
    pass


class BusinessRuleException(Exception):
    """
    Exceção lançada quando uma regra de negócio é violada.
    """
    pass