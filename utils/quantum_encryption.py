"""
Quantum Encryption Utilities
============================

This module provides encryption and decryption utilities that work with
quantum-generated keys from BB84 protocol. It includes simple XOR encryption
and more advanced encryption schemes for educational purposes.
"""

import hashlib
import secrets
from typing import List, Union, Tuple
import json


def bits_to_bytes(bits: List[int]) -> bytes:
    """Convert a list of bits to bytes"""
    if len(bits) % 8 != 0:
        # Pad with zeros to make it divisible by 8
        bits = bits + [0] * (8 - (len(bits) % 8))
    
    byte_array = []
    for i in range(0, len(bits), 8):
        byte_val = 0
        for j in range(8):
            if i + j < len(bits):
                byte_val |= (bits[i + j] << (7 - j))
        byte_array.append(byte_val)
    
    return bytes(byte_array)


def bytes_to_bits(data: bytes) -> List[int]:
    """Convert bytes to a list of bits"""
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


def quantum_xor_encrypt(message: str, quantum_key: List[int]) -> Tuple[bytes, dict]:
    """
    Encrypt a message using XOR with a quantum-generated key.
    
    Args:
        message: The message to encrypt
        quantum_key: List of bits from BB84 protocol
    
    Returns:
        Tuple of (encrypted_bytes, metadata)
    """
    message_bytes = message.encode('utf-8')
    message_bits = bytes_to_bits(message_bytes)
    
    # Ensure we have enough key material
    if len(quantum_key) < len(message_bits):
        raise ValueError(f"Quantum key too short: need {len(message_bits)} bits, have {len(quantum_key)}")
    
    # XOR message bits with quantum key
    encrypted_bits = []
    for i, bit in enumerate(message_bits):
        encrypted_bits.append(bit ^ quantum_key[i])
    
    encrypted_bytes = bits_to_bytes(encrypted_bits)
    
    metadata = {
        "original_length": len(message),
        "message_bits": len(message_bits),
        "key_bits_used": len(message_bits),
        "encryption_method": "quantum_xor"
    }
    
    return encrypted_bytes, metadata


def quantum_xor_decrypt(encrypted_bytes: bytes, quantum_key: List[int], metadata: dict) -> str:
    """
    Decrypt a message using XOR with a quantum-generated key.
    
    Args:
        encrypted_bytes: The encrypted message
        quantum_key: List of bits from BB84 protocol (same as used for encryption)
        metadata: Metadata from encryption process
    
    Returns:
        Decrypted message string
    """
    encrypted_bits = bytes_to_bits(encrypted_bytes)
    key_bits_used = metadata.get("key_bits_used", len(encrypted_bits))
    
    # XOR encrypted bits with quantum key
    decrypted_bits = []
    for i in range(key_bits_used):
        if i < len(encrypted_bits) and i < len(quantum_key):
            decrypted_bits.append(encrypted_bits[i] ^ quantum_key[i])
    
    # Convert back to bytes and then to string
    decrypted_bytes = bits_to_bytes(decrypted_bits)
    
    # Trim to original length
    original_length = metadata.get("original_length", len(decrypted_bytes))
    decrypted_message = decrypted_bytes.decode('utf-8', errors='ignore')[:original_length]
    
    return decrypted_message


def one_time_pad_encrypt(message: str, quantum_key: List[int]) -> Tuple[bytes, dict]:
    """
    Implement One-Time Pad encryption using quantum key.
    This provides perfect secrecy when used correctly.
    
    Args:
        message: The message to encrypt
        quantum_key: List of bits from BB84 protocol
    
    Returns:
        Tuple of (encrypted_bytes, metadata)
    """
    if not quantum_key:
        raise ValueError("Quantum key cannot be empty")
    
    message_bytes = message.encode('utf-8')
    
    # Ensure we have enough key material (critical for OTP security)
    if len(quantum_key) < len(message_bytes) * 8:
        raise ValueError(f"Insufficient key material for OTP: need {len(message_bytes) * 8} bits, have {len(quantum_key)}")
    
    encrypted_bytes = bytearray()
    key_index = 0
    
    for byte in message_bytes:
        # XOR each bit of the byte with key bits
        encrypted_byte = 0
        for bit_pos in range(8):
            message_bit = (byte >> (7 - bit_pos)) & 1
            key_bit = quantum_key[key_index] if key_index < len(quantum_key) else 0
            encrypted_bit = message_bit ^ key_bit
            encrypted_byte |= (encrypted_bit << (7 - bit_pos))
            key_index += 1
        
        encrypted_bytes.append(encrypted_byte)
    
    metadata = {
        "original_length": len(message),
        "key_bits_used": key_index,
        "encryption_method": "one_time_pad",
        "perfectly_secure": key_index <= len(quantum_key)
    }
    
    return bytes(encrypted_bytes), metadata


def one_time_pad_decrypt(encrypted_bytes: bytes, quantum_key: List[int], metadata: dict) -> str:
    """
    Decrypt One-Time Pad encrypted message.
    
    Args:
        encrypted_bytes: The encrypted message
        quantum_key: List of bits from BB84 protocol (same as used for encryption)
        metadata: Metadata from encryption process
    
    Returns:
        Decrypted message string
    """
    decrypted_bytes = bytearray()
    key_index = 0
    
    for byte in encrypted_bytes:
        # XOR each bit of the encrypted byte with key bits
        decrypted_byte = 0
        for bit_pos in range(8):
            encrypted_bit = (byte >> (7 - bit_pos)) & 1
            key_bit = quantum_key[key_index] if key_index < len(quantum_key) else 0
            decrypted_bit = encrypted_bit ^ key_bit
            decrypted_byte |= (decrypted_bit << (7 - bit_pos))
            key_index += 1
        
        decrypted_bytes.append(decrypted_byte)
    
    # Trim to original length
    original_length = metadata.get("original_length", len(decrypted_bytes))
    decrypted_message = decrypted_bytes.decode('utf-8', errors='ignore')[:original_length]
    
    return decrypted_message


def generate_key_hash(quantum_key: List[int]) -> str:
    """Generate a hash of the quantum key for verification purposes"""
    key_bytes = bits_to_bytes(quantum_key)
    return hashlib.sha256(key_bytes).hexdigest()


def verify_key_integrity(quantum_key: List[int], expected_hash: str) -> bool:
    """Verify that a quantum key hasn't been tampered with"""
    actual_hash = generate_key_hash(quantum_key)
    return actual_hash == expected_hash


class QuantumSecureMessenger:
    """
    A secure messenger that uses quantum-generated keys for encryption.
    Demonstrates practical application of BB84-generated keys.
    """
    
    def __init__(self, alice_key: List[int], bob_key: List[int]):
        """
        Initialize messenger with quantum keys from BB84.
        
        Args:
            alice_key: Alice's quantum key from BB84
            bob_key: Bob's quantum key from BB84
        """
        if alice_key != bob_key:
            raise ValueError("Alice and Bob keys don't match! QKD may have failed.")
        
        self.shared_key = alice_key
        self.key_hash = generate_key_hash(self.shared_key)
        self.messages_sent = []
        self.key_usage = 0  # Track how much key has been used
        
        print(f"🔐 Quantum Secure Messenger initialized")
        print(f"   Shared key length: {len(self.shared_key)} bits")
        print(f"   Key hash: {self.key_hash[:16]}...")
    
    def send_message(self, sender: str, message: str, encryption_method: str = "quantum_xor") -> dict:
        """
        Send an encrypted message using the quantum key.
        
        Args:
            sender: Name of sender ("Alice" or "Bob")
            message: Message to encrypt and send
            encryption_method: "quantum_xor" or "one_time_pad"
        
        Returns:
            Dictionary with encrypted message and metadata
        """
        if self.key_usage >= len(self.shared_key):
            raise ValueError("Quantum key exhausted! Need to perform QKD again.")
        
        # Use portion of key that hasn't been used yet
        available_key = self.shared_key[self.key_usage:]
        
        try:
            if encryption_method == "one_time_pad":
                encrypted_bytes, metadata = one_time_pad_encrypt(message, available_key)
            else:
                encrypted_bytes, metadata = quantum_xor_encrypt(message, available_key)
            
            # Update key usage
            self.key_usage += metadata["key_bits_used"]
            
            message_data = {
                "sender": sender,
                "timestamp": __import__('time').time(),
                "encrypted_message": encrypted_bytes.hex(),
                "metadata": metadata,
                "encryption_method": encryption_method,
                "key_usage_after": self.key_usage
            }
            
            self.messages_sent.append(message_data)
            
            print(f"📤 {sender} sent encrypted message:")
            print(f"   Original: {message}")
            print(f"   Encrypted: {encrypted_bytes.hex()}")
            print(f"   Key bits used: {metadata['key_bits_used']}")
            print(f"   Remaining key: {len(self.shared_key) - self.key_usage} bits")
            
            return message_data
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            raise
    
    def receive_message(self, message_data: dict, receiver: str) -> str:
        """
        Decrypt and receive a message.
        
        Args:
            message_data: Encrypted message data from send_message
            receiver: Name of receiver ("Alice" or "Bob")
        
        Returns:
            Decrypted message string
        """
        try:
            encrypted_bytes = bytes.fromhex(message_data["encrypted_message"])
            metadata = message_data["metadata"]
            encryption_method = message_data["encryption_method"]
            
            # Calculate which part of key was used
            key_bits_used = metadata["key_bits_used"]
            key_start = message_data["key_usage_after"] - key_bits_used
            key_portion = self.shared_key[key_start:message_data["key_usage_after"]]
            
            if encryption_method == "one_time_pad":
                decrypted_message = one_time_pad_decrypt(encrypted_bytes, key_portion, metadata)
            else:
                decrypted_message = quantum_xor_decrypt(encrypted_bytes, key_portion, metadata)
            
            print(f"📥 {receiver} received message:")
            print(f"   From: {message_data['sender']}")
            print(f"   Decrypted: {decrypted_message}")
            
            return decrypted_message
            
        except Exception as e:
            print(f"❌ Failed to decrypt message: {e}")
            raise
    
    def get_key_statistics(self) -> dict:
        """Get statistics about key usage"""
        return {
            "total_key_bits": len(self.shared_key),
            "bits_used": self.key_usage,
            "bits_remaining": len(self.shared_key) - self.key_usage,
            "usage_percentage": (self.key_usage / len(self.shared_key)) * 100,
            "messages_sent": len(self.messages_sent),
            "key_hash": self.key_hash
        }
    
    def save_conversation(self, filename: str = "quantum_conversation.json"):
        """Save the encrypted conversation to a file"""
        conversation_data = {
            "key_statistics": self.get_key_statistics(),
            "messages": self.messages_sent,
            "participants": ["Alice", "Bob"],
            "protocol": "BB84 + Quantum Encryption"
        }
        
        with open(filename, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        print(f"💾 Conversation saved to {filename}")


def demonstrate_quantum_encryption(alice_key: List[int], bob_key: List[int]):
    """
    Demonstrate quantum encryption with keys from BB84.
    
    Args:
        alice_key: Alice's quantum key from BB84
        bob_key: Bob's quantum key from BB84
    """
    print("\n🔐 QUANTUM ENCRYPTION DEMONSTRATION")
    print("="*50)
    
    try:
        # Create secure messenger
        messenger = QuantumSecureMessenger(alice_key, bob_key)
        
        # Test messages
        test_messages = [
            ("Alice", "Hello Bob! Our quantum channel is secure! 🔐"),
            ("Bob", "Hi Alice! BB84 worked perfectly! ⚛️"),
            ("Alice", "Let's share some secret data: Password123!"),
            ("Bob", "Received! Quantum cryptography is amazing! 🎉")
        ]
        
        # Send and receive messages
        conversation = []
        for sender, message in test_messages:
            # Send message
            message_data = messenger.send_message(sender, message, "quantum_xor")
            
            # Receive message (simulate other party receiving)
            receiver = "Bob" if sender == "Alice" else "Alice"
            decrypted = messenger.receive_message(message_data, receiver)
            
            conversation.append({
                "sender": sender,
                "receiver": receiver,
                "original": message,
                "decrypted": decrypted,
                "success": message == decrypted
            })
            
            print()
        
        # Show statistics
        stats = messenger.get_key_statistics()
        print(f"\n📊 ENCRYPTION STATISTICS:")
        print(f"   Total key bits: {stats['total_key_bits']}")
        print(f"   Bits used: {stats['bits_used']} ({stats['usage_percentage']:.1f}%)")
        print(f"   Messages sent: {stats['messages_sent']}")
        print(f"   All messages decrypted correctly: {all(msg['success'] for msg in conversation)}")
        
        # Save conversation
        messenger.save_conversation()
        
        print("\n✅ Quantum encryption demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quantum encryption demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test with sample keys
    print("🧪 Testing Quantum Encryption Utilities")
    
    # Generate sample quantum keys (normally from BB84)
    sample_key = [random.randint(0, 1) for _ in range(256)]
    
    # Test basic encryption
    message = "Hello, Quantum World! 🌍"
    encrypted, metadata = quantum_xor_encrypt(message, sample_key)
    decrypted = quantum_xor_decrypt(encrypted, sample_key, metadata)
    
    print(f"Original: {message}")
    print(f"Encrypted: {encrypted.hex()}")
    print(f"Decrypted: {decrypted}")
    print(f"Success: {message == decrypted}")
    
    # Test secure messenger
    demonstrate_quantum_encryption(sample_key, sample_key.copy())
