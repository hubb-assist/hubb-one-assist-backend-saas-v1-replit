import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash
    
    Args:
        plain_password: Senha em texto puro
        hashed_password: Hash da senha armazenado
        
    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

# Testar verificação com o hash do banco de dados
password = "admin123"
stored_hash = "$2b$12$FYUAKSYjCUND6lH2eSTiv.XIyALi10AlrNctuXSXSwlLHGWFMJ5gW"

is_valid = verify_password(password, stored_hash)
print(f"Senha '{password}' é válida para o hash: {is_valid}")