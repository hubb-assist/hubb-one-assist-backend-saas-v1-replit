import bcrypt

def get_password_hash(password: str) -> str:
    """
    Gera hash da senha usando bcrypt
    
    Args:
        password: Senha em texto puro
        
    Returns:
        str: Hash da senha
    """
    # Gerar salt e hash com bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

# Gerar hash para a senha 'admin123'
password = "admin123"
hashed_password = get_password_hash(password)
print(f"Hash para '{password}': {hashed_password}")