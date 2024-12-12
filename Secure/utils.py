import pickle


with open('./Secure/keys/public_key.pkl', 'rb') as f:
    public_key = pickle.load(f)

with open('./Secure/keys/private_key.pkl', 'rb') as f:
    private_key = pickle.load(f)


def encrypt_data(data: str) -> str:
    data_as_int = int.from_bytes(data.encode(), 'big')
    encrypted_data = public_key.encrypt(data_as_int)
    return str(encrypted_data.ciphertext())

def decrypt_data(encrypted_data: str) -> str:
    encrypted_data_as_int = int(encrypted_data)
    decrypted_data_as_int = private_key.decrypt(encrypted_data_as_int)
    decrypted_data = decrypted_data_as_int.to_bytes((decrypted_data_as_int.bit_length() + 7) // 8, 'big').decode()
    return decrypted_data
