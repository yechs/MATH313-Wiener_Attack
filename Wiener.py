#!/usr/bin/env python3

from typing import Tuple

import rsa
from sympy import Symbol, solve

from ContinuedFraction import ContinuedFraction
from libs.RSAvulnerableKeyGenerator import generateKeys


class Wiener:
    def __init__(self,
                 n: int or None = None,
                 e: int or None = None,
                 nbits: int = 1024):
        """
        Initializes a class for demonstrating Wiener's Attack (small private
        exponent attack) on RSA.

        You can either supply the class with your own public key (N,e) to try
        it out in a real scenario, or leave them blank to let the program
        generate a keypair vulnerable to the attack.

        In the latter case, you can use the nbits parameter to state how many
        bits (how strong) you want the key size to be. The larger the key
        size, the more complicated the calculation (and thus longer time). If
        you leave it blank, a default key size value of 1024 bits will be
        used. However in reality, it is more common to use 2048 or 4096 bits.

        :param n: the modulus N of your given RSA key
        :param e: the public exponent e of your given RSA key
        :param nbits: size of generated vulnerable RSA key. Default to 1024.
        """
        print("=" * 20, "Initialization", "=" * 20)

        if n is None or e is None:
            print("[!] No public key given. Will generate a new keypair.")
            n, e = self._generateKeys(nbits)

        # the local variable n is in lowercase to comply with naming conventions
        self.N = n
        self.e = e

        # Will be used to store encrypted ciphertext
        self.enc_message: bytes or None = None

        print("=" * 20, "Initialization", "=" * 20)

    def _generateKeys(self, nbits: int) -> Tuple[int, int]:
        """
        An internal method called to generate an RSA keypair vulnerable to
        Wiener's Attack. The nbits parameter is passed down from the __init__
        method.

        :param nbits: size of generated vulnerable RSA key.
        :return: the public key (N,e)
        """

        # Note that during keypair generation, the records of p and q are
        # destroyed as they are only intermediate variables and the leak of
        # which will render the keypair vulnerable.
        e, n, d = generateKeys(nbits)

        print("[+] Generated an RSA keypair vulnerable to Wiener's attack.")
        print("N:\t", n)
        print("e:\t", e)
        print("d:\t", d)

        # We will not return the private exponent d, which is highly
        # secretive and unknown to attacker.
        return n, e

    def encrypt(self, message: str or None = None) -> bytes:
        """
        Encrypts a message with the public key stored in the class.

        :param message: The message for encryption. Leave it blank to prompt
                        for user input.
        :return: The encrypted message in binary bytes
        """
        print("\n" + "=" * 20, "Encryption", "=" * 20)

        print("Let's say Alex owns the private key and publishes the public "
              "key so that others can send him messages only he can decrypt.")

        print("Now, Ye uses the public key to send Alex an encrypted message.")

        if message is None:
            # No message entered, prompt for user input
            message = input("[+] Message Content: ")
        else:
            print("[+] Message Content:", message)

        # Here the message is first encoded from a string into byte using UTF-8
        pubkey = rsa.PublicKey(self.N, self.e)
        enc_message = rsa.encrypt(message.encode("utf8"), pubkey)

        # The encrypted bytes is converted into hexadecimal digits to print out.
        print("[+] Encrypted Message (hex):\t", enc_message.hex())

        # Only the ciphertext is stored at the class level, since only Ye
        # knows the original text message.
        self.enc_message = enc_message

        print("=" * 20, "Encryption", "=" * 20)

        return enc_message

    def crack(self) -> Tuple[int, int, int, int]:
        """
        Cracks the RSA cipher using Wiener's Attack. It uses properties of
        continued fractions to guess the value of k/d using the convergents
        of k/N. Detailed proof is given in our presentation.

        :return: Cracked RSA private key defined by (p, q, d, φ(N))
        """
        print("\n" + "=" * 20, "CRACKING", "=" * 20)

        print("As attacker, we intercepted the encrypted message.")
        print("We also have knowledge of the public key (N,e).")

        print("Let us now apply Wiener's Attack to the known public key.")
        print("To do so, we are going to approximate d through the continued "
              "fraction expansion of e/N")

        input("Press Enter to start cracking...")

        # the local variable n is in lowercase to comply with naming conventions
        e, n = self.e, self.N

        cf = ContinuedFraction(e, n)
        expansions = cf.expansion()
        print("\n[+] Found the continued fraction expansion of e/N")
        print(expansions)

        # See the slides for detailed proof
        print("\nAs demonstrated in slides, we will use these coefficients to "
              "recursively calculate the convergents of e/N, and use these "
              "convergents to approximate k/d and guess their values.")
        print("To verify that our guess is correct, we will go through the "
              "following steps \n"
              "1. Calculate φ(N) = (ed-1)/k\n"
              "2. Solve the equation x^2 - (N-φ(N)+1)x + N = 0. "
              "Ideally, p and q will be the two roots.\n"
              "3. We will use the property N=pq to verify that.")

        input("Press Enter to start iterating over convergents...")

        convergents = cf.convergents_iter()

        # a flag indicating whether the attack works
        solved = False

        # The convergent efficiently approximates e/N, which is then be used to
        # approximate k/d. That is why we name them as k_guess and d_guess.
        # See the slides for detailed proof.
        for k_guess, d_guess in convergents:
            print(f"[+] Trying k/d = {k_guess} / {d_guess}", end="\t")

            if k_guess == 0:
                # invalid
                print("INCORRECT")
                continue

            # Recall that k * φ(N) = ed - 1 (because ed ≡ 1 (mod φ(N)))
            # With (N,e) known and (k,d) approximated, we can deduce φ(N)
            phi_guess = (e * d_guess - 1) // k_guess

            # We use sympy to solve this equation.
            # See the slides for why p and q are roots.
            x = Symbol('x', integer=True)
            roots = solve(x ** 2 + (phi_guess - n - 1) * x + n, x)

            # There should be exactly two roots (p and q are distinct primes)
            # if not, we proceed to the next attempted guess of k/d
            if len(roots) != 2:
                print("INCORRECT")
                continue

            # We verify if the guess works by multiplying the roots, which
            # should give us N
            p_guess, q_guess = roots
            if p_guess * q_guess != n:
                # This (p,q) pair is incorrect, proceed to next attempted guess
                print("INCORRECT")
                continue

            print('\n\n[+] This guess worked! It gives us:')
            print("p:\t", p_guess)
            print("q:\t", q_guess)
            print("N:\t", n)
            print("e:\t", e)
            print("d:\t", d_guess)
            print('φ(N):', phi_guess)

            # Cracked the private key! Breaking out of the iteration
            solved = True
            break

        if not solved:
            print("[-] Wiener's Attack failed")
            raise Exception("Wiener's Attack failed")

        print("=" * 20, "CRACKING", "=" * 20)
        return p_guess, q_guess, d_guess, phi_guess

    def decrypt(self, enc_message: bytes or None = None) -> str:
        """
        Decrypt the message by cracking the cipher.

        :param enc_message: The message to be decrypted. Leave it blank to use
                            the message we encrypted in self.encrypt()
        :return: The decrypted message
        """

        if enc_message is None:
            if self.enc_message is None:
                raise Exception("An encrypted message is needed for decryption")
            enc_message = self.enc_message

        # Call the method to crack the cipher
        p_guess, q_guess, d_guess, _ = self.crack()

        print("\n" + "=" * 20, "Decrypt the private message", "=" * 20)
        print("Since we have now cracked the private key (N,d), let's use it "
              "to decrypt the private message sent to Alex!")

        # Technically, only (N,d) is needed to recover the message, but the
        # library I use requires all variables to instantiate the
        # rsa.PrivateKey class.
        privkey = rsa.PrivateKey(self.N, self.e, d_guess, p_guess, q_guess)
        dec_message = rsa.decrypt(enc_message, privkey).decode("utf8")
        print("[+] Decrypted Message:\t", dec_message)

        print("=" * 20, "Decrypt the private message", "=" * 20)
        return dec_message


if __name__ == '__main__':
    w = Wiener()

    w.encrypt()
    w.decrypt()

    print("\nYay! 🎉")
