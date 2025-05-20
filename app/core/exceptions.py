"""
Exceções customizadas para a aplicação.
"""


class EntityNotFoundException(Exception):
    """
    Exceção lançada quando uma entidade não é encontrada.
    """
    pass


class BusinessRuleViolationException(Exception):
    """
    Exceção lançada quando uma regra de negócio é violada.
    """
    pass


class PermissionDeniedException(Exception):
    """
    Exceção lançada quando um usuário não tem permissão para uma operação.
    """
    pass


class ValidationException(Exception):
    """
    Exceção lançada quando a validação de dados falha.
    """
    pass