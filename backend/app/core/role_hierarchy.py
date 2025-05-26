"""
Definição hierárquica de permissões por papel (role) no sistema.
Determina quais permissões são atribuídas automaticamente a cada papel.
"""

from app.db.models import UserRole

# Definições de permissões do sistema
# Permissões relacionadas a pacientes
PERMISSION_CREATE_PATIENT = "CAN_CREATE_PATIENT"
PERMISSION_VIEW_PATIENT = "CAN_VIEW_PATIENT"
PERMISSION_EDIT_PATIENT = "CAN_EDIT_PATIENT"
PERMISSION_DELETE_PATIENT = "CAN_DELETE_PATIENT"

# Agrupamentos úteis de permissões
ALL_PATIENT_PERMISSIONS = [
    PERMISSION_CREATE_PATIENT,
    PERMISSION_VIEW_PATIENT,
    PERMISSION_EDIT_PATIENT,
    PERMISSION_DELETE_PATIENT
]

# Mapeamento de permissões por papel
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        # Super admin tem todas as permissões do sistema
        *ALL_PATIENT_PERMISSIONS,
        # Adicionar outras permissões aqui conforme o sistema expandir
    ],
    
    UserRole.DIRETOR: [
        # Diretor tem acesso similar ao Super Admin
        *ALL_PATIENT_PERMISSIONS,
        # Adicionar outras permissões aqui conforme o sistema expandir
    ],
    
    UserRole.DONO_ASSINANTE: [
        # Dono de clínica tem acesso total a recursos relacionados à sua clínica
        *ALL_PATIENT_PERMISSIONS,
        # Adicionar outras permissões aqui conforme o sistema expandir
    ],
    
    UserRole.COLABORADOR_NIVEL_2: [
        # Colaborador tem permissões limitadas
        PERMISSION_CREATE_PATIENT,
        PERMISSION_VIEW_PATIENT,
        # Adicionar outras permissões aqui conforme o sistema expandir
    ]
}

def get_permissions_for_role(role: UserRole) -> list:
    """
    Obtém a lista de permissões para um determinado papel (role).
    
    Args:
        role: O papel do usuário (da enumeração UserRole)
        
    Returns:
        list: Lista de strings com as permissões associadas ao papel
    """
    if role is None:
        return []
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user: dict, permission: str) -> bool:
    """
    Verifica se um usuário tem uma determinada permissão.
    Considera tanto o papel do usuário quanto permissões personalizadas.
    
    Args:
        user: Objeto do usuário ou dicionário com informações do usuário
        permission: A permissão a ser verificada
        
    Returns:
        bool: True se o usuário tem a permissão, False caso contrário
    """
    user_role = getattr(user, "role", None)
    
    # Se o usuário for super admin ou diretor, tem todas as permissões
    if user_role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        return True
    
    # Verificar nas permissões do papel
    role_permissions = get_permissions_for_role(user_role)
    if permission in role_permissions:
        return True
    
    # Verificar nas permissões personalizadas do usuário, se existirem
    custom_permissions = getattr(user, "custom_permissions", [])
    if permission in custom_permissions:
        return True
    
    return False